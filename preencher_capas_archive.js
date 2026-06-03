const fs = require('fs');

const catalogPath = 'docs/GAMES_format.json';
const start = Number(process.argv[2] || 0);
const limit = Number(process.argv[3] || 0);
const data = JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
const entries = Object.entries(data.DATA);
const slice = entries.slice(start, limit ? start + limit : undefined);
const thumbCache = new Map();

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function cleanTitle(name) {
    return String(name || '')
        .replace(/\s+-\s+\[[^\]]+\].*$/g, '')
        .replace(/\s+\[[^\]]+\]\s*$/g, '')
        .replace(/\s+/g, ' ')
        .trim();
}

function normalizeTitle(value) {
    return String(value || '')
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
        .replace(/[™®©]/g, '')
        .replace(/&/g, ' and ')
        .replace(/[^a-z0-9]+/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
}

function titleTokens(value) {
    const stop = new Set(['a', 'an', 'and', 'de', 'do', 'da', 'of', 'the', 'to', 'in', 'for', 'with']);
    return normalizeTitle(value).split(' ').filter(token => token && !stop.has(token));
}

function scoreCandidate(target, candidate) {
    const targetNorm = normalizeTitle(target);
    const candidateNorm = normalizeTitle(candidate.title);
    if (!targetNorm || !candidateNorm) return 0;
    if (targetNorm === candidateNorm) return 1.2;

    const targetTokens = titleTokens(target);
    const candidateTokens = titleTokens(candidate.title);
    if (!targetTokens.length || !candidateTokens.length) return 0;

    const candidateSet = new Set(candidateTokens);
    const common = targetTokens.filter(token => candidateSet.has(token)).length;
    let score = common / targetTokens.length;

    if (candidateNorm.includes(targetNorm) || targetNorm.includes(candidateNorm)) score += 0.2;
    if (candidate.mediatype === 'software' || candidate.mediatype === 'image') score += 0.12;
    if (candidate.mediatype === 'movies') score += 0.04;
    if (candidate.index === 1) score += 0.04;

    const extra = candidateTokens.filter(token => !targetTokens.includes(token)).length;
    score -= Math.min(0.18, extra * 0.025);

    return score;
}

async function archiveSearch(query, rows = 12) {
    const params = new URLSearchParams();
    params.set('q', query);
    params.append('fl[]', 'identifier');
    params.append('fl[]', 'title');
    params.append('fl[]', 'mediatype');
    params.set('rows', String(rows));
    params.set('output', 'json');

    const response = await fetch(`https://archive.org/advancedsearch.php?${params}`, {
        headers: { 'User-Agent': 'LojaPS4/1.0' }
    });

    if (!response.ok) return [];
    const payload = await response.json();
    return payload.response && Array.isArray(payload.response.docs) ? payload.response.docs : [];
}

async function hasArchiveThumbnail(identifier) {
    if (thumbCache.has(identifier)) return thumbCache.get(identifier);

    const imageUrl = `https://archive.org/services/img/${encodeURIComponent(identifier)}`;
    let ok = false;

    try {
        const response = await fetch(imageUrl, {
            method: 'HEAD',
            redirect: 'follow',
            headers: { 'User-Agent': 'LojaPS4/1.0' }
        });

        const finalUrl = response.url || '';
        const contentType = response.headers.get('content-type') || '';
        ok = response.ok && contentType.includes('image') && !finalUrl.includes('/images/notfound');
    } catch (error) {
        ok = false;
    }

    thumbCache.set(identifier, ok);
    return ok;
}

async function findArchiveCover(title) {
    const safeTitle = title.replace(/"/g, ' ');
    const queries = [
        `title:("${safeTitle}") AND (mediatype:software OR mediatype:image)`,
        `title:("${safeTitle}")`,
        `"${safeTitle}"`
    ];

    const seen = new Set();
    const candidates = [];

    for (const query of queries) {
        const docs = await archiveSearch(query);
        for (const doc of docs) {
            if (!doc.identifier || seen.has(doc.identifier)) continue;
            seen.add(doc.identifier);
            const score = scoreCandidate(title, doc);
            if (score >= 0.58) candidates.push({ ...doc, score });
        }
        if (candidates.length) break;
        await sleep(120);
    }

    candidates.sort((a, b) => b.score - a.score);

    for (const candidate of candidates.slice(0, 8)) {
        if (await hasArchiveThumbnail(candidate.identifier)) {
            return {
                url: `https://archive.org/services/img/${encodeURIComponent(candidate.identifier)}`,
                id: candidate.identifier,
                title: candidate.title,
                score: candidate.score
            };
        }
        await sleep(80);
    }

    return null;
}

async function main() {
    let matched = 0;
    let checked = 0;
    const misses = [];

    for (const [, game] of slice) {
        checked += 1;
        if (game.cover_url) continue;

        const title = cleanTitle(game.name);
        const cover = await findArchiveCover(title);

        if (cover) {
            game.cover_url = cover.url;
            game.cover_source = 'archive.org';
            game.cover_source_id = cover.id;
            matched += 1;
        } else {
            misses.push(title);
        }

        if (checked % 25 === 0) {
            console.log(`${start + checked}/${entries.length} verificados, ${matched} capas adicionadas neste lote`);
        }

        await sleep(140);
    }

    fs.writeFileSync(catalogPath, JSON.stringify(data, null, 2) + '\n');
    console.log(`Lote ${start}-${start + slice.length}: ${matched} capas adicionadas, ${misses.length} sem capa.`);
    if (misses.length) console.log(`Sem capa exemplos: ${misses.slice(0, 10).join(' | ')}`);
}

main().catch(error => {
    console.error(error);
    process.exit(1);
});
