// PS4 Gamepad Controller Support
// Provides full DualShock 4 controller integration for PS4 browser

(function() {
    'use strict';
    
    // Controller state
    let gamepadIndex = null;
    let lastButtonState = {};
    let scrollSpeed = 0;
    let isPolling = false;
    
    // Button mappings for DualShock 4
    const BUTTONS = {
        X: 0,           // Confirm/Select
        CIRCLE: 1,      // Back/Cancel
        SQUARE: 2,      // Toggle view
        TRIANGLE: 3,    // Search
        L1: 4,          // Page up
        R1: 5,          // Page down
        L2: 6,          // Not used
        R2: 7,          // Not used
        SHARE: 8,       // Not used
        OPTIONS: 9,     // Menu
        L3: 10,         // Not used
        R3: 11,         // Not used
        DPAD_UP: 12,    // Navigate up
        DPAD_DOWN: 13,  // Navigate down
        DPAD_LEFT: 14,  // Navigate left
        DPAD_RIGHT: 15, // Navigate right
        PS: 16          // PS button
    };
    
    // Axis mappings
    const AXES = {
        LEFT_X: 0,
        LEFT_Y: 1,
        RIGHT_X: 2,
        RIGHT_Y: 3
    };
    
    // Configuration
    const CONFIG = {
        deadzone: 0.15,
        scrollMultiplier: 15,
        debounceTime: 150,
        pollInterval: 16 // ~60 FPS
    };
    
    // Debounce state
    let lastButtonPress = {};
    
    // Initialize controller support
    function init() {
        console.log('[Gamepad] Initializing controller support...');
        
        // Listen for gamepad connection
        window.addEventListener('gamepadconnected', onGamepadConnected);
        window.addEventListener('gamepaddisconnected', onGamepadDisconnected);
        
        // Check for already connected gamepads
        const gamepads = navigator.getGamepads ? navigator.getGamepads() : [];
        for (let i = 0; i < gamepads.length; i++) {
            if (gamepads[i]) {
                onGamepadConnected({ gamepad: gamepads[i] });
                break;
            }
        }
        
        console.log('[Gamepad] Controller support initialized');
    }
    
    // Gamepad connected handler
    function onGamepadConnected(event) {
        const gamepad = event.gamepad;
        console.log('[Gamepad] Controller connected:', gamepad.id);
        
        gamepadIndex = gamepad.index;
        showControllerHint(true);
        
        if (!isPolling) {
            isPolling = true;
            pollGamepad();
        }
    }
    
    // Gamepad disconnected handler
    function onGamepadDisconnected(event) {
        console.log('[Gamepad] Controller disconnected:', event.gamepad.id);
        
        if (event.gamepad.index === gamepadIndex) {
            gamepadIndex = null;
            showControllerHint(false);
            isPolling = false;
        }
    }
    
    // Show/hide controller hint
    function showControllerHint(connected) {
        let hint = document.getElementById('controller-hint');
        
        if (!hint) {
            hint = document.createElement('div');
            hint.id = 'controller-hint';
            hint.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: rgba(0, 0, 0, 0.8);
                color: #00d4ff;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 16px;
                z-index: 10000;
                font-family: Arial, sans-serif;
                border: 1px solid #00d4ff;
                transition: opacity 0.3s;
            `;
            document.body.appendChild(hint);
        }
        
        if (connected) {
            hint.innerHTML = '🎮 Controle conectado | △ Buscar | ○ Topo | X Selecionar';
            hint.style.opacity = '1';
            setTimeout(() => { hint.style.opacity = '0.6'; }, 3000);
        } else {
            hint.innerHTML = '🎮 Controle desconectado';
            hint.style.opacity = '1';
            setTimeout(() => { hint.style.opacity = '0'; }, 2000);
        }
    }
    
    // Main polling loop
    function pollGamepad() {
        if (!isPolling || gamepadIndex === null) return;
        
        const gamepads = navigator.getGamepads ? navigator.getGamepads() : [];
        const gamepad = gamepads[gamepadIndex];
        
        if (!gamepad) {
            requestAnimationFrame(pollGamepad);
            return;
        }
        
        // Process buttons
        processButtons(gamepad);
        
        // Process axes (analog sticks)
        processAxes(gamepad);
        
        // Continue polling
        requestAnimationFrame(pollGamepad);
    }
    
    // Process button inputs
    function processButtons(gamepad) {
        const now = Date.now();
        
        for (const [name, index] of Object.entries(BUTTONS)) {
            const button = gamepad.buttons[index];
            const isPressed = button && (button.pressed || button.value > 0.5);
            const wasPressed = lastButtonState[index];
            
            // Button just pressed (not held)
            if (isPressed && !wasPressed) {
                // Debounce check
                if (now - (lastButtonPress[index] || 0) > CONFIG.debounceTime) {
                    lastButtonPress[index] = now;
                    handleButtonPress(name);
                }
            }
            
            lastButtonState[index] = isPressed;
        }
    }
    
    // Handle button press actions
    function handleButtonPress(buttonName) {
        console.log('[Gamepad] Button pressed:', buttonName);
        
        switch (buttonName) {
            case 'X':
                // Confirm/Select - click focused element or first visible button
                clickFocusedOrFirst();
                break;
                
            case 'CIRCLE':
                // Back to top
                window.scrollTo({ top: 0, behavior: 'smooth' });
                break;
                
            case 'TRIANGLE':
                // Focus search input
                focusSearch();
                break;
                
            case 'SQUARE':
                // Toggle view (if implemented)
                break;
                
            case 'L1':
                // Page up
                window.scrollBy({ top: -window.innerHeight * 0.8, behavior: 'smooth' });
                break;
                
            case 'R1':
                // Page down
                window.scrollBy({ top: window.innerHeight * 0.8, behavior: 'smooth' });
                break;
                
            case 'DPAD_UP':
                navigateItems(-1);
                break;
                
            case 'DPAD_DOWN':
                navigateItems(1);
                break;
                
            case 'DPAD_LEFT':
                navigateItems(-4); // Previous row
                break;
                
            case 'DPAD_RIGHT':
                navigateItems(4); // Next row
                break;
                
            case 'OPTIONS':
                // Menu (could open settings)
                break;
        }
    }
    
    // Process analog stick axes
    function processAxes(gamepad) {
        // Left stick Y-axis for scrolling
        const leftY = gamepad.axes[AXES.LEFT_Y];
        
        if (Math.abs(leftY) > CONFIG.deadzone) {
            scrollSpeed = leftY * CONFIG.scrollMultiplier;
            window.scrollBy(0, scrollSpeed);
        }
        
        // Right stick for faster scrolling
        const rightY = gamepad.axes[AXES.RIGHT_Y];
        
        if (Math.abs(rightY) > CONFIG.deadzone) {
            window.scrollBy(0, rightY * CONFIG.scrollMultiplier * 2);
        }
    }
    
    // Click focused element or first button
    function clickFocusedOrFirst() {
        // Try to click focused element
        const focused = document.querySelector('.game-card.focused, .game-item.focused, [data-focused="true"]');
        if (focused) {
            const btn = focused.querySelector('a, button');
            if (btn) {
                btn.click();
                return;
            }
        }
        
        // Click active element if it's a link or button
        if (document.activeElement && (document.activeElement.tagName === 'A' || document.activeElement.tagName === 'BUTTON')) {
            document.activeElement.click();
            return;
        }
        
        // Find first visible game link
        const gameLinks = document.querySelectorAll('.game-card a, .download-btn, .game-item a');
        for (const link of gameLinks) {
            const rect = link.getBoundingClientRect();
            if (rect.top >= 0 && rect.top < window.innerHeight) {
                link.click();
                return;
            }
        }
    }
    
    // Focus search input
    function focusSearch() {
        const searchInput = document.querySelector('#searchInput, input[type="search"], input[type="text"]');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
    
    // Navigate between items
    let currentFocusIndex = -1;
    
    function navigateItems(direction) {
        const items = document.querySelectorAll('.game-card, .game-item, .letter-section');
        if (items.length === 0) return;
        
        // Remove previous focus
        items.forEach(item => {
            item.classList.remove('focused');
            item.removeAttribute('data-focused');
        });
        
        // Calculate new index
        currentFocusIndex += direction;
        
        // Wrap around
        if (currentFocusIndex < 0) currentFocusIndex = items.length - 1;
        if (currentFocusIndex >= items.length) currentFocusIndex = 0;
        
        // Focus new item
        const newItem = items[currentFocusIndex];
        if (newItem) {
            newItem.classList.add('focused');
            newItem.setAttribute('data-focused', 'true');
            newItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    // Add focus styles
    function addFocusStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .game-card.focused,
            .game-item.focused,
            [data-focused="true"] {
                outline: 3px solid #00d4ff !important;
                outline-offset: 4px;
                transform: scale(1.02);
                transition: all 0.15s ease;
                box-shadow: 0 0 20px rgba(0, 212, 255, 0.4) !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            addFocusStyles();
            init();
        });
    } else {
        addFocusStyles();
        init();
    }
    
    // Export for debugging
    window.PS4Controller = {
        init,
        isConnected: () => gamepadIndex !== null,
        getConfig: () => CONFIG
    };
    
})();
