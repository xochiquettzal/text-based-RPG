document.addEventListener('DOMContentLoaded', () => {
    // Screen Containers
    const worldSelectionContainer = document.getElementById('world-selection-container');
    const raceInfoContainer = document.getElementById('race-info-container'); // Animal Kingdom
    const darkFantasyInfoContainer = document.getElementById('dark-fantasy-info-container'); // Dark Fantasy
    const gameScreenWrapper = document.getElementById('game-screen-wrapper'); 
    const gameContainer = document.querySelector('#game-screen-wrapper .container'); 

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
    const API_PREFIX = '/api/v1'; 
    // let currentPlayerState = null; // No longer needed, state managed by backend via session_id
    let currentSessionId = null; // Store the session ID
    let currentOnConfirm = null; 

    // --- Core API and UI Functions ---

    async function fetchStory(endpoint, payload = null) {
        const fullEndpoint = `${API_PREFIX}${endpoint}`;
        console.log(`Fetching: ${API_BASE_URL}${fullEndpoint}`); 

        try {
            // No longer need to inject player_state here
            const options = {
                method: payload ? 'POST' : 'GET',
                headers: { 'Content-Type': 'application/json', },
            };
            if (payload) {
                options.body = JSON.stringify(payload);
            }
            const response = await fetch(`${API_BASE_URL}${fullEndpoint}`, options); 
            if (!response.ok) {
                 // Try to parse error response from API if available
                 let errorDetail = `HTTP error! status: ${response.status}`;
                 try {
                     const errorJson = await response.json();
                     errorDetail = errorJson.detail || errorDetail;
                 } catch (parseError) { /* Ignore if response is not JSON */ }
                 throw new Error(errorDetail);
            }
            return await response.json();
        } catch (error) {
            console.error("API isteği başarısız:", error);
            if (chatLog) {
                 addMessageToChatLog(`Hata: ${error.message}`, "ai-error");
            }
            if (choicesContainer) {
                choicesContainer.innerHTML = ''; 
            }
            // Maybe disable input on critical error?
            // setInputDisabledState(true); 
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
    // Now accepts playerInfo object directly from response
    function updateCharacterCard(playerInfo) {
        if (!playerInfo || !characterInfoCard) return;

        charNameElement.textContent = playerInfo.name || 'Bilinmiyor';
        // Use alias 'class_name' if needed, Pydantic handles alias on response
        charClassElement.textContent = playerInfo.class_name || 'Belirsiz'; 
        charHealthElement.textContent = playerInfo.health !== undefined ? playerInfo.health : '??';

        charStatsList.innerHTML = ''; 
        if (playerInfo.stats) {
            for (const [statName, statValue] of Object.entries(playerInfo.stats)) {
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

    // Updated to handle new response structure
    function displayStory(responseData) {
        if (!responseData) return;
        
        // Update card with info from response
        if (responseData.player_info_for_card) {
            updateCharacterCard(responseData.player_info_for_card); 
        }
        
        addMessageToChatLog(responseData.text, 'ai'); 
        choicesContainer.innerHTML = ''; 
        if (responseData.choices && responseData.choices.length > 0) {
            responseData.choices.forEach(choice => {
                const button = document.createElement('button');
                button.textContent = choice.text;
                button.dataset.choiceId = choice.id; 
                // Pass session_id implicitly via global variable
                button.addEventListener('click', () => handleChoice(choice.id, choice.text)); 
                choicesContainer.appendChild(button);
            });
        } else {
            const endMessage = document.createElement('p');
            endMessage.textContent = responseData.end_message || "Devam edecek...";
            choicesContainer.appendChild(endMessage);
        }
    }

    // Updated to send session_id instead of player_state
    async function handleChoice(choiceId, choiceText) { 
        if (!currentSessionId) {
            addMessageToChatLog("Hata: Geçerli bir oyun oturumu bulunamadı!", "ai-error");
            return;
        }
        addMessageToChatLog(choiceText, 'player'); 
        choicesContainer.innerHTML = ''; 
        addTypingIndicator(); 
        setInputDisabledState(true);
        const payload = { 
            session_id: currentSessionId, // Send session ID
            choice_id: choiceId, 
            choice_text: choiceText, 
            // player_state: currentPlayerState // Removed
        };
        const responseData = await fetchStory('/make_choice', payload); 
        removeTypingIndicator(); 
        if (responseData) {
            // DisplayStory now handles updating the card from responseData.player_info_for_card
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

    // Updated to store session_id and handle new response structure
    async function startGame(selectedWorldId, selectedClassOrFactionId = null) { 
        addMessageToChatLog("Oyun başlatılıyor...", "system"); 
        setInputDisabledState(true);
        // Card is initially hidden, updateCharacterCard called by displayStory will show it
        // if(characterInfoCard) characterInfoCard.style.display = 'block'; 
        
        const startPayload = {
            player_name: "Kaşif", 
            world_id: selectedWorldId,
            selected_class_or_faction: selectedClassOrFactionId 
        };
        const initialResponseData = await fetchStory('/start_game', startPayload); 
        
        if (chatLog && chatLog.lastChild && chatLog.lastChild.classList.contains('system-message')) {
             chatLog.removeChild(chatLog.lastChild);
        }
        if (initialResponseData && initialResponseData.session_id) {
            currentSessionId = initialResponseData.session_id; // Store the session ID
            console.log("Game started with session ID:", currentSessionId); // Debug log
            // Display initial story and update card
            displayStory(initialResponseData); 
        } else {
             addMessageToChatLog(`Oyun başlatılamadı. ${initialResponseData?.error || ''}`, "ai-error");
             // Maybe show world selection again?
             // initializeApp(); // Careful with recursion
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
