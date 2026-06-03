# -*- coding: utf-8 -*-
"""
Gerador de param.sfo para PS4 PKG
Execute: python gerar_sfo.py
"""

import struct
import os

def create_param_sfo(output_path, params):
    """
    Cria um arquivo param.sfo válido para PS4
    """
    
    # Ordenar parâmetros alfabeticamente (requisito do PS4)
    sorted_params = sorted(params.items())
    
    # Header
    magic = b'\x00PSF'
    version = struct.pack('<I', 0x00000101)  # Version 1.1
    
    # Calcular offsets
    key_table_offset = 0x14 + (len(sorted_params) * 0x10)  # Header + Index entries
    
    # Construir key table
    key_table = b''
    key_offsets = []
    for key, _ in sorted_params:
        key_offsets.append(len(key_table))
        key_table += key.encode('utf-8') + b'\x00'
    
    # Padding para alinhamento de 4 bytes
    while len(key_table) % 4 != 0:
        key_table += b'\x00'
    
    data_table_offset = key_table_offset + len(key_table)
    
    # Construir data table e index entries
    data_table = b''
    index_entries = b''
    data_offsets = []
    
    for i, (key, value) in enumerate(sorted_params):
        data_offsets.append(len(data_table))
        
        if isinstance(value, int):
            # Integer (4 bytes)
            fmt = 0x0404  # INT32
            data = struct.pack('<I', value)
            data_len = 4
            max_len = 4
        else:
            # String (UTF-8)
            fmt = 0x0204  # UTF-8 String
            data = value.encode('utf-8') + b'\x00'
            data_len = len(data)
            # Max length com padding
            max_len = ((data_len + 3) // 4) * 4
            if max_len < 8:
                max_len = 8
            # Padding
            data += b'\x00' * (max_len - data_len)
        
        data_table += data
        
        # Index entry (16 bytes)
        index_entries += struct.pack('<H', key_offsets[i])  # Key offset
        index_entries += struct.pack('<H', fmt)              # Data format
        index_entries += struct.pack('<I', data_len)         # Data len
        index_entries += struct.pack('<I', max_len)          # Max len
        index_entries += struct.pack('<I', data_offsets[i])  # Data offset
    
    # Header completo
    header = magic
    header += version
    header += struct.pack('<I', key_table_offset)
    header += struct.pack('<I', data_table_offset)
    header += struct.pack('<I', len(sorted_params))
    
    # Montar arquivo final
    sfo_data = header + index_entries + key_table + data_table
    
    # Salvar
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(sfo_data)
    
    print(f"✅ param.sfo criado: {output_path}")
    print(f"   Tamanho: {len(sfo_data)} bytes")
    return sfo_data

def main():
    # Parâmetros do aplicativo PS4 Games Store
    params = {
        'APP_TYPE': 1,
        'APP_VER': '01.00',
        'ATTRIBUTE': 0,
        'CATEGORY': 'gd',
        'CONTENT_ID': 'UP0001-CUSA99999_00-PS4GAMESSTORE001',
        'DOWNLOAD_DATA_SIZE': 0,
        'FORMAT': 'obs',
        'PARENTAL_LEVEL': 0,
        'SYSTEM_VER': 0,
        'TITLE': 'PS4 Games Store',
        'TITLE_ID': 'CUSA99999',
        'VERSION': '01.00',
    }
    
    # Caminho de saída
    output_path = os.path.join(os.path.dirname(__file__), 'sce_sys', 'param.sfo')
    
    # Criar o arquivo
    create_param_sfo(output_path, params)
    
    print("\n📦 Próximos passos:")
    print("1. Adicione icon0.png (512x512) em sce_sys/")
    print("2. Opcional: Adicione pic1.png (1920x1080) em sce_sys/")
    print("3. Use Fake PKG Tools para criar o PKG final")

if __name__ == '__main__':
    main()
