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

    // Dice Roll Overlay Elements
    const diceRollOverlay = document.getElementById('dice-roll-overlay');
    const animatedDie = document.getElementById('animated-die');
    const dieNumberDisplay = document.getElementById('die-number-display'); 
    const diceResultText = document.getElementById('dice-result-text');

    const API_BASE_URL = 'http://127.0.0.1:8000'; 
    const API_PREFIX = '/api/v1'; 
    let currentSessionId = null; 
    let currentOnConfirm = null; 
    let diceCycleInterval = null; 

    async function fetchStory(endpoint, payload = null) {
        const fullEndpoint = `${API_PREFIX}${endpoint}`;
        console.log(`Fetching: ${API_BASE_URL}${fullEndpoint}`); 

        try {
            const options = {
                method: payload ? 'POST' : 'GET',
                headers: { 'Content-Type': 'application/json', },
            };
            if (payload) {
                options.body = JSON.stringify(payload);
            }
            const response = await fetch(`${API_BASE_URL}${fullEndpoint}`, options); 
            if (!response.ok) {
                 let errorDetail = `HTTP error! status: ${response.status}`;
                 try {
                     const errorJson = await response.json();
                     errorDetail = errorJson.detail || errorDetail;
                 } catch (parseError) { /* Ignore */ }
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
    
    function updateCharacterCard(playerInfo) {
        if (!playerInfo || !characterInfoCard) return;
        charNameElement.textContent = playerInfo.name || 'Bilinmiyor';
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

    function displayStory(responseData) {
        if (!responseData) return;
        if (responseData.player_info_for_card) {
            updateCharacterCard(responseData.player_info_for_card); 
        }
        addMessageToChatLog(responseData.text, 'ai'); 
        choicesContainer.innerHTML = ''; 
        if (responseData.choices && responseData.choices.length > 0) {
            responseData.choices.forEach(choice => {
                const button = document.createElement('button');
                let buttonText = choice.text;
                if (choice.skill_check_stat && choice.skill_check_dc !== undefined) {
                    const displayStat = choice.skill_check_stat.charAt(0).toUpperCase() + choice.skill_check_stat.slice(1);
                    buttonText += ` (${displayStat} DC${choice.skill_check_dc})`;
                }
                button.textContent = buttonText;
                button.dataset.choiceId = choice.id;
                button.addEventListener('click', () => handleChoice(choice)); 
                choicesContainer.appendChild(button);
            });
        } else {
            const endMessage = document.createElement('p');
            endMessage.textContent = responseData.end_message || "Devam edecek...";
            choicesContainer.appendChild(endMessage);
        }
    }

    function showDiceRollOutcome(resultDetails) {
        if (!diceRollOverlay || !animatedDie || !dieNumberDisplay || !diceResultText || !resultDetails) return;

        clearInterval(diceCycleInterval); 

        if (dieNumberDisplay) dieNumberDisplay.textContent = resultDetails.roll;
        if (animatedDie) {
            animatedDie.classList.remove('rolling-anticipation', 'rolling-cycle');
            animatedDie.classList.add('rolling-reveal'); 
        }
        
        setTimeout(() => {
            if (animatedDie) {
                animatedDie.classList.remove('rolling-reveal');
                animatedDie.classList.add('number-revealed'); 
            }
            if(diceResultText) diceResultText.classList.add('visible');
            if(diceRollOverlay) diceRollOverlay.classList.add('text-visible'); // For smooth die shift
        }, 400); // Match CSS reveal animation duration 

        let outcomeHTML = `<strong>Yetenek Kontrolü: ${resultDetails.stat_checked.charAt(0).toUpperCase() + resultDetails.stat_checked.slice(1)}</strong><br>`;
        outcomeHTML += `<span class="roll-details">Atılan Zar: ${resultDetails.roll} (Doğal)<br>`;
        outcomeHTML += `Bonus: ${resultDetails.modifier >= 0 ? '+' : ''}${resultDetails.modifier}<br>`;
        outcomeHTML += `Toplam: ${resultDetails.total_roll} vs DC: ${resultDetails.dc}</span><br>`;
        outcomeHTML += `<span class="outcome-text outcome-${resultDetails.outcome.replace(' ', '_')}">${resultDetails.outcome}</span>`;
        
        diceResultText.innerHTML = outcomeHTML;
    }

    async function handleChoice(choice) { 
        if (!currentSessionId) {
            addMessageToChatLog("Hata: Geçerli bir oyun oturumu bulunamadı!", "ai-error");
            return;
        }

        const isSkillCheck = choice.skill_check_stat && choice.skill_check_dc !== undefined;
        const choiceTextForLog = choice.text; 

        addMessageToChatLog(choiceTextForLog, 'player');
        choicesContainer.innerHTML = '';
        setInputDisabledState(true); 

        if (isSkillCheck) {
            if (diceRollOverlay && animatedDie && dieNumberDisplay && diceResultText) {
                diceResultText.classList.remove('visible'); 
                diceRollOverlay.classList.remove('text-visible'); // Reset for die shift
                dieNumberDisplay.textContent = ''; 
                animatedDie.className = 'die'; // Reset to base class
                animatedDie.classList.add('rolling-anticipation');
                diceRollOverlay.classList.remove('hidden');
                
                addMessageToChatLog(`${choice.text} için zar atılıyor...`, 'system');

                setTimeout(() => {
                    if (animatedDie && dieNumberDisplay) {
                        animatedDie.classList.remove('rolling-anticipation');
                        animatedDie.classList.add('rolling-cycle');
                        diceCycleInterval = setInterval(() => {
                            if(dieNumberDisplay) dieNumberDisplay.textContent = Math.floor(Math.random() * 20) + 1;
                        }, 70); 
                    }
                }, 500); 
            }
            setTimeout(addTypingIndicator, 700); 
        } else {
            addTypingIndicator();
        }
        
        const payload = { 
            session_id: currentSessionId,
            choice_id: choice.id, 
            choice_text: choice.text, 
        };

        const fetchDelay = isSkillCheck ? 1500 : 0; 
        
        setTimeout(async () => {
            const responseData = await fetchStory('/make_choice', payload); 
            removeTypingIndicator(); 
            clearInterval(diceCycleInterval); 

            if (isSkillCheck && animatedDie) {
                animatedDie.classList.remove('rolling-anticipation', 'rolling-cycle');
            }

            if (responseData) {
                if (responseData.skill_check_result) {
                    showDiceRollOutcome(responseData.skill_check_result);
                    if (diceRollOverlay) {
                        const proceedAfterOverlay = () => {
                            diceRollOverlay.classList.add('hidden');
                            diceRollOverlay.classList.remove('text-visible'); // Reset for die shift
                            if(animatedDie) animatedDie.className = 'die'; 
                            if(dieNumberDisplay) dieNumberDisplay.textContent = '';
                            if(diceResultText) diceResultText.classList.remove('visible');
                            displayStory(responseData); 
                            setInputDisabledState(false);
                            if (playerCommandInput) playerCommandInput.focus();
                        };
                        diceRollOverlay.addEventListener('click', proceedAfterOverlay, { once: true });
                    }
                } else {
                    displayStory(responseData);
                    setInputDisabledState(false);
                    if (playerCommandInput) playerCommandInput.focus();
                }
            } else { 
                setInputDisabledState(false);
                if (isSkillCheck && diceRollOverlay) { 
                    diceRollOverlay.classList.add('hidden');
                    diceRollOverlay.classList.remove('text-visible');
                    if(animatedDie) animatedDie.className = 'die';
                    if(dieNumberDisplay) dieNumberDisplay.textContent = '';
                    if(diceResultText) diceResultText.classList.remove('visible');
                }
            }
        }, fetchDelay);
    }

    async function handleCustomAction() {
        const actionText = playerCommandInput.value.trim();
        if (!actionText) return;
        playerCommandInput.value = ''; 
        await handleChoice({ id: "USER_ACTION", text: actionText });
    }

    async function startGame(selectedWorldId, selectedClassOrFactionId = null) { 
        addMessageToChatLog("Oyun başlatılıyor...", "system"); 
        setInputDisabledState(true);
        
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
            currentSessionId = initialResponseData.session_id; 
            console.log("Game started with session ID:", currentSessionId); 
            displayStory(initialResponseData); 
        } else {
             addMessageToChatLog(`Oyun başlatılamadı. ${initialResponseData?.error || ''}`, "ai-error");
        }
        setInputDisabledState(false);
        if (playerCommandInput) playerCommandInput.focus();
    }

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

    function initializeApp() {
        if (gameScreenWrapper) gameScreenWrapper.style.display = 'none'; 
        if (raceInfoContainer) raceInfoContainer.style.display = 'none';
        if (darkFantasyInfoContainer) darkFantasyInfoContainer.style.display = 'none'; 
        if (characterInfoCard) characterInfoCard.style.display = 'none'; 
        if (worldSelectionContainer) worldSelectionContainer.style.display = 'block'; 

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

    initializeApp(); 
});
