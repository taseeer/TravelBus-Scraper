// voiceAssistant.js
class VoiceAssistant {
    constructor() {
        this.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        this.recognition.lang = 'en-US';
        this.recognition.continuous = false;
        this.recognition.interimResults = false;

        // Common city name corrections
        this.cityCorrections = {
            'lahore': 'Lahore',
            'multan': 'Multan',
            'islamabad': 'Islamabad',
            'karachi': 'Karachi',
            'faisalabad': 'Faisalabad',
            'rawalpindi': 'Rawalpindi',
            'peshawar': 'Peshawar',
            'quetta': 'Quetta',
            'sialkot': 'Sialkot',
            'hyderabad': 'Hyderabad',
            'lahore thokar': 'Lahore Thokar',
            'abbottabad':'Abbottabad',
            // Add more cities as needed
        };

        // Voice command patterns
        this.commandPatterns = [
            /(?:from|book from|travel from)\s+([a-zA-Z\s]+)\s+(?:to)\s+([a-zA-Z\s]+)/i,
            /([a-zA-Z\s]+)\s+(?:to)\s+([a-zA-Z\s]+)/i
        ];
    }

    init(departureDropdown, destinationDropdown, dateInput, searchButton) {
        this.departureDropdown = departureDropdown;
        this.destinationDropdown = destinationDropdown;
        this.dateInput = dateInput;
        this.searchButton = searchButton;

        // Setup recognition handlers
        this.setupRecognitionHandlers();
    }

    setupRecognitionHandlers() {
        this.recognition.onstart = () => {
            // Show listening indicator
            this.updateStatus('Listening...', 'text-primary');
        };

        this.recognition.onresult = (event) => {
            const voiceText = event.results[0][0].transcript.toLowerCase();
            console.log('Voice input:', voiceText);
            this.processVoiceCommand(voiceText);
        };

        this.recognition.onerror = (event) => {
            console.error('Voice recognition error:', event.error);
            this.updateStatus('Error: ' + event.error, 'text-danger');
        };

        this.recognition.onend = () => {
            this.updateStatus('Voice recognition ended', 'text-muted');
            setTimeout(() => this.clearStatus(), 2000);
        };
    }

    startListening() {
        try {
            this.recognition.start();
        } catch (error) {
            console.error('Error starting voice recognition:', error);
            this.updateStatus('Error starting voice recognition', 'text-danger');
        }
    }

    processVoiceCommand(voiceText) {
        let matched = false;

        // Try each command pattern
        for (const pattern of this.commandPatterns) {
            const match = voiceText.match(pattern);
            if (match) {
                matched = true;
                const [_, departure, destination] = match;
                this.handleCitySelection(departure.trim(), destination.trim());
                break;
            }
        }

        if (!matched) {
            this.updateStatus('Please say "from [city] to [city]"', 'text-warning');
        }
    }

    handleCitySelection(departure, destination) {
        // Correct city names
        departure = this.correctCityName(departure);
        destination = this.correctCityName(destination);

        // Validate cities exist in dropdowns
        const departureExists = this.cityExistsInDropdown(departure, this.departureDropdown);
        const destinationExists = this.cityExistsInDropdown(destination, this.destinationDropdown);

        if (departureExists && destinationExists) {
            // Set values in dropdowns
            this.departureDropdown.value = departure;
            this.destinationDropdown.value = destination;

            // Set today's date if not already set
            if (!this.dateInput.value) {
                this.dateInput.value = new Date().toISOString().split('T')[0];
            }

            this.updateStatus(`Selected: ${departure} to ${destination}`, 'text-success');
            
            // Trigger search
            setTimeout(() => this.searchButton.click(), 1000);
        } else {
            let errorMessage = 'City not found: ';
            if (!departureExists) errorMessage += departure;
            if (!destinationExists) errorMessage += ((!departureExists ? ' and ' : '') + destination);
            this.updateStatus(errorMessage, 'text-danger');
        }
    }

    correctCityName(city) {
        const lowercaseCity = city.toLowerCase();
        return this.cityCorrections[lowercaseCity] || this.capitalizeFirstLetter(city);
    }

    cityExistsInDropdown(city, dropdown) {
        return Array.from(dropdown.options).some(
            option => option.value.toLowerCase() === city.toLowerCase()
        );
    }

    capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
    }

    updateStatus(message, className = 'text-primary') {
        let statusElement = document.getElementById('voice-status');
        if (!statusElement) {
            statusElement = document.createElement('div');
            statusElement.id = 'voice-status';
            document.getElementById('voice-btn').insertAdjacentElement('afterend', statusElement);
        }
        statusElement.className = className + ' mt-2 text-center';
        statusElement.textContent = message;
    }

    clearStatus() {
        const statusElement = document.getElementById('voice-status');
        if (statusElement) {
            statusElement.textContent = '';
        }
    }
}

// Export the class
export default VoiceAssistant;