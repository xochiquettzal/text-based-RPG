document.addEventListener('DOMContentLoaded', () => {
    // Screen Containers
    const worldSelectionContainer = document.getElementById('world-selection-container');
    const raceInfoContainer = document.getElementById('race-info-container'); // Animal Kingdom
    const darkFantasyInfoContainer = document.getElementById('dark-fantasy-info-container'); // Dark Fantasy
    const gameScreenWrapper = document.getElementById('game-screen-wrapper'); // New wrapper for game screen
    const gameContainer = document.querySelector('#game-screen-wrapper .container'); // Game chat container inside wrapper

    // Modal Elements
    const confirmationModal = document.getElementById('confirmation-modal');
    const modalMessage = document.getElementById('modal-message');
    const modalConfirmButton = document.getElementById('modal-confirm-button');
    const modalCancelButton = document.getElementById('modal-cancel-button');

    // Game Container Elements
    const worldTitleElement = document.getElementById('world-title');
    const chatLogContainer = document.getElementById('chat-log-container');
    const chatLog = document.getElementById('chat-log');
    const choicesContainer = document.getElementById('choices-container');
    const playerCommandInput = document.getElementById('player-command');
    const sendCommandButton = document.getElementById('send-command');

    // Character Info Card Elements
    const characterInfoCard = document.getElementById('character-info-card');
    const charNameElement = document.getElementById('char-name');
    const charClassElement = document.getElementById('char-class');
    const charHealthElement = document.getElementById('char-health');
    const charStatsList = document.getElementById('char-stats');

    const API_BASE_URL = 'http://127.0.0.1:8000'; 
    let currentPlayerState = null; 
    let currentOnConfirm = null; 

    // --- Core API and UI Functions ---

    async function fetchStory(endpoint, payload = null) {
        try {
            if (payload && endpoint !== '/start_game' && currentPlayerState) {
                payload.player_state = currentPlayerState;
            }
            const options = {
                method: payload ? 'POST' : 'GET',
                headers: { 'Content-Type': 'application/json', },
            };
            if (payload) {
                options.body = JSON.stringify(payload);
            }
            const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error("API isteği başarısız:", error);
            if (chatLog) {
                 addMessageToChatLog("Hata: Oyun sunucusuna bağlanılamadı. Lütfen daha sonra tekrar deneyin.", "ai-error");
            }
            if (choicesContainer) {
                choicesContainer.innerHTML = ''; 
            }
            return null;
        }
    }

    function addMessageToChatLog(text, senderType) { 
        if (!chatLog) return; 
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', `${senderType}-message`);
        messageDiv.textContent = text; 
        chatLog.appendChild(messageDiv);
        if (chatLogContainer) {
            chatLogContainer.scrollTop = chatLogContainer.scrollHeight; 
        }
    }

    function addTypingIndicator() {
        if (!chatLog) return;
        const indicatorDiv = document.createElement('div');
        indicatorDiv.classList.add('chat-message', 'ai-message', 'typing-indicator-message');
        indicatorDiv.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
        chatLog.appendChild(indicatorDiv);
        if (chatLogContainer) {
            chatLogContainer.scrollTop = chatLogContainer.scrollHeight;
        }
    }

    function removeTypingIndicator() {
        if (!chatLog) return;
        const indicator = chatLog.querySelector('.typing-indicator-message');
        if (indicator) {
            chatLog.removeChild(indicator);
        }
    }

    function setInputDisabledState(disabled) {
        if (playerCommandInput) playerCommandInput.disabled = disabled;
        if (sendCommandButton) sendCommandButton.disabled = disabled;
        if (choicesContainer) {
            choicesContainer.querySelectorAll('button').forEach(button => {
                button.disabled = disabled;
            });
        }
    }
    
    // --- Character Card Update ---
    function updateCharacterCard(playerState) {
        if (!playerState || !characterInfoCard) return;

        charNameElement.textContent = playerState.name || 'Bilinmiyor';
        charClassElement.textContent = playerState.class || 'Belirsiz';
        charHealthElement.textContent = playerState.health !== undefined ? playerState.health : '??';

        charStatsList.innerHTML = ''; 
        if (playerState.stats) {
            for (const [statName, statValue] of Object.entries(playerState.stats)) {
                const li = document.createElement('li');
                const strong = document.createElement('strong');
                strong.textContent = `${statName.toUpperCase()}: `;
                const span = document.createElement('span');
                span.textContent = statValue;
                li.appendChild(strong);
                li.appendChild(span);
                charStatsList.appendChild(li);
            }
        }
        characterInfoCard.style.display = 'block'; 
    }
    // --- End Character Card Update ---

    function displayStory(responseData) {
        if (!responseData) return;
        if (responseData.player_state) {
            currentPlayerState = responseData.player_state;
            updateCharacterCard(currentPlayerState); 
        }
        addMessageToChatLog(responseData.text, 'ai'); 
        choicesContainer.innerHTML = ''; 
        if (responseData.choices && responseData.choices.length > 0) {
            responseData.choices.forEach(choice => {
                const button = document.createElement('button');
                button.textContent = choice.text;
                button.dataset.choiceId = choice.id; 
                button.addEventListener('click', () => handleChoice(choice.id, choice.text));
                choicesContainer.appendChild(button);
            });
        } else {
            const endMessage = document.createElement('p');
            endMessage.textContent = responseData.end_message || "Devam edecek...";
            choicesContainer.appendChild(endMessage);
        }
    }

    async function handleChoice(choiceId, choiceText) { 
        addMessageToChatLog(choiceText, 'player'); 
        choicesContainer.innerHTML = ''; 
        addTypingIndicator(); 
        setInputDisabledState(true);
        const payload = { 
            choice_id: choiceId, 
            choice_text: choiceText, 
            player_state: currentPlayerState 
        };
        const responseData = await fetchStory('/make_choice', payload);
        removeTypingIndicator(); 
        if (responseData) {
            displayStory(responseData); 
        }
        setInputDisabledState(false);
        playerCommandInput.focus(); 
    }

    async function handleCustomAction() {
        const actionText = playerCommandInput.value.trim();
        if (!actionText) return;
        playerCommandInput.value = ''; 
        await handleChoice("USER_ACTION", actionText);
    }

    // Modified startGame to accept worldId and optional selectedClassOrFactionId
    async function startGame(selectedWorldId, selectedClassOrFactionId = null) { 
        addMessageToChatLog("Oyun başlatılıyor...", "system"); 
        setInputDisabledState(true);
        // Ensure card is visible when game starts (updateCharacterCard will also set display:block)
        if(characterInfoCard) characterInfoCard.style.display = 'block'; 
        
        const startPayload = {
            player_name: "Kaşif", 
            world_id: selectedWorldId,
            selected_class_or_faction: selectedClassOrFactionId 
        };
        const initialResponseData = await fetchStory('/start_game', startPayload); 
        
        // Remove "Oyun başlatılıyor..." message
        if (chatLog && chatLog.lastChild && chatLog.lastChild.classList.contains('system-message')) {
             chatLog.removeChild(chatLog.lastChild);
        }
        if (initialResponseData) {
            // displayStory will handle updating the card via currentPlayerState
            displayStory(initialResponseData); 
        } else {
             addMessageToChatLog("Oyun başlatılamadı.", "ai-error");
        }
        setInputDisabledState(false);
        if (playerCommandInput) playerCommandInput.focus();
    }

    // --- Modal Logic ---
    function showModal(message, onConfirmCallback) {
        if (!confirmationModal || !modalMessage) return;
        modalMessage.textContent = message;
        currentOnConfirm = onConfirmCallback; 
        confirmationModal.style.display = 'flex'; 
    }

    function hideModal() {
         if (!confirmationModal) return;
        confirmationModal.style.display = 'none';
        currentOnConfirm = null; 
    }
    // --- End Modal Logic ---

    // --- Listener Setup for Info Cards --- 
    function addRaceCardListeners(worldId, worldName) {
        if (!raceInfoContainer) return;
        raceInfoContainer.querySelectorAll('.race-info-card').forEach(raceCard => {
            const newCard = raceCard.cloneNode(true); 
            raceCard.parentNode.replaceChild(newCard, raceCard);

            newCard.addEventListener('click', () => {
                const raceId = newCard.dataset.raceId;
                const raceName = newCard.querySelector('h2').textContent; 
                showModal(`'${raceName}' ırkını seçmek istediğine emin misin?`, async () => {
                    raceInfoContainer.style.display = 'none'; 
                    if (gameContainer) {
                        gameContainer.classList.remove('bg-dark-fantasy', 'bg-animal-kingdom'); 
                        gameContainer.classList.add(`bg-${worldId}`); 
                    }
                    if (gameScreenWrapper) gameScreenWrapper.style.display = 'flex'; 
                    if (worldTitleElement) worldTitleElement.textContent = worldName; 
                    await startGame(worldId, raceId); 
                });
            });
        });
    }

     function addFactionCardListeners(worldId, worldName) {
        if (!darkFantasyInfoContainer) return;
        darkFantasyInfoContainer.querySelectorAll('.faction-info-card').forEach(factionCard => {
            const newCard = factionCard.cloneNode(true); 
            factionCard.parentNode.replaceChild(newCard, factionCard);

            newCard.addEventListener('click', () => {
                const factionId = newCard.dataset.factionId;
                const factionName = newCard.querySelector('h2').textContent; 
                showModal(`'${factionName}' fraksiyonunu seçmek istediğine emin misin?`, async () => {
                    darkFantasyInfoContainer.style.display = 'none'; 
                     if (gameContainer) {
                        gameContainer.classList.remove('bg-dark-fantasy', 'bg-animal-kingdom'); 
                        gameContainer.classList.add(`bg-${worldId}`); 
                    }
                    if (gameScreenWrapper) gameScreenWrapper.style.display = 'flex'; 
                    if (worldTitleElement) worldTitleElement.textContent = worldName; 
                    await startGame(worldId, factionId); 
                });
            });
        });
    }
    // --- End Listener Setup ---

    // --- Initialization ---
    function initializeApp() {
        // Ensure all main screen containers are hidden initially, show world selection
        if (gameScreenWrapper) gameScreenWrapper.style.display = 'none'; 
        if (raceInfoContainer) raceInfoContainer.style.display = 'none';
        if (darkFantasyInfoContainer) darkFantasyInfoContainer.style.display = 'none'; 
        if (characterInfoCard) characterInfoCard.style.display = 'none'; 
        if (worldSelectionContainer) worldSelectionContainer.style.display = 'block'; 

        // Add listeners to world cards
        const worldCardsContainer = document.getElementById('world-cards-container'); 
        if (worldCardsContainer) {
            const worldCards = worldCardsContainer.querySelectorAll('.world-card'); 
            worldCards.forEach(card => {
                card.addEventListener('click', () => { 
                    const worldId = card.dataset.worldId;
                    const worldName = card.dataset.worldName; 

                    if (worldSelectionContainer) worldSelectionContainer.style.display = 'none'; 

                    if (worldId === 'animal_kingdom') {
                        if (raceInfoContainer) raceInfoContainer.style.display = 'flex'; 
                        addRaceCardListeners(worldId, worldName); 
                    } else if (worldId === 'dark_fantasy') {
                        if (darkFantasyInfoContainer) darkFantasyInfoContainer.style.display = 'flex'; 
                        addFactionCardListeners(worldId, worldName); 
                    } 
                });
            });
        }

        // Add listeners for modal buttons
        if (modalConfirmButton) {
            modalConfirmButton.addEventListener('click', () => {
                if (currentOnConfirm) {
                    currentOnConfirm(); 
                }
                hideModal();
            });
        }
        if (modalCancelButton) {
            modalCancelButton.addEventListener('click', hideModal);
        }

        // Add listeners for custom text input
        if (sendCommandButton) {
            sendCommandButton.addEventListener('click', handleCustomAction);
        }
        if (playerCommandInput) {
            playerCommandInput.addEventListener('keypress', (event) => {
                if (event.key === 'Enter') {
                    event.preventDefault(); 
                    handleCustomAction();
                }
            });
        }
    }

    // Start the application initialization
    initializeApp(); 
});
