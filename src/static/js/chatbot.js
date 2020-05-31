$(document).ready(function(){
	$("#input-field").focus();
});


var app = new Vue({
    el: '#app',
    data: {
        message: "",
        isSpeaking: false,
        speaking: false,
        dialog: false,
        transcript: "",
        messages: [
            {
                is_system: true,
                message: "Dear valued customer, I am Coco. How can I help you?",
                time: new Date().toLocaleTimeString()
            }
        ],
        response: {
            countries: [],
            classes: []
        },
        form: {
            place_to: "",
            place_from: "",
            date_departure: "",
            date_return: "",
            flight_class: "",
            flight_stop: "",
            is_round_trip: null
        }
    },
    mounted:function(){
        this.get();
        this.checkSpeechCompatibility();
    },
    computed: {
        speechRecognition() {
            return window.SpeechRecognition || window.webkitSpeechRecognition;
        },
        recognition() {
            return this.speechRecognition?new this.speechRecognition():false;
        },
        messageBody() {
            return document.getElementById("message-body");
        }
    },
    methods: {
        get: function(){
            axios.get("/api/countries").then((response) => {
                this.response.countries = response.data.countries;
                this.response.classes = response.data.classes;
            });
        },
        sendMessage: function(e){
            if(e.keyCode === 13 && !e.shiftKey && this.message){
                e.preventDefault();
                this.messages.push({"message": this.message, "is_system": false, time: new Date().toLocaleTimeString()});
                var message = this.message;
                this.message = "";
                this.updateWindowSize(false);
                axios.get("/api/query", {
                    params: {
                        message: message
                    }
                }).then((response) => {
                    response.data.messages.forEach((item) => {
                        this.messages.push({"message": item.message, "is_system": true, time: item.time});
                        tts(item.message);
                        this.updateWindowSize(true);
                    });
                    this.bindPlace(response.data);
                    this.bindDate(response.data);
                    this.bindTrip(response.data);
                    this.bindClass(response.data);
                    this.bindStop(response.data);
                    this.bindIsNew(response.data)
                });
            }
        },
        bindPlace: function(item){
            if(item.place_from){
                this.form.place_from = item.place_from;
            }

            if(item.place_to){
                this.form.place_to = item.place_to;
            }
        },
        bindDate: function(item){
            if(item.date_departure){
                this.form.date_departure = item.date_departure;
            }

            if(item.date_return){
                this.form.date_return = item.date_return;
            }
        },
        bindTrip: function(item){
            this.form.is_round_trip = item.is_round_trip;
            console.log("this.form = ", this.form);
        },
        bindClass: function(item){
            if(item.class_type){
                this.form.flight_class = item.class_type;
            }
        },
        bindStop: function(item){
            if(item.connection_limit){
                this.form.flight_stop = item.connection_limit;
            }
        },
        bindIsNew: function(item){
            if(item.is_new_from_place){
                this.form.is_new_from_place = item.is_new_from_place;
            }
            if(item.is_new_from_date){
                this.form.is_new_from_date = item.is_new_from_date;
            }
            if(item.is_new_to_place){
                this.form.is_new_to_place = item.is_new_to_place;
            }
            if(item.is_new_return_date){
                this.form.is_new_return_date = item.is_new_return_date;
            }
            if(item.is_new_round_trip){
                this.form.is_new_round_trip = item.is_new_round_trip;
            }
            if(item.is_new_connection){
                this.form.is_new_connection = item.is_new_connection;
            }
            if(item.is_new_class){
                this.form.is_new_class = item.is_new_class;
            }
        },
        selected: function(item, selectedItem){
            return item === selectedItem;
        },
        checkSpeechCompatibility(){
            if(!this.recognition){
                this.$emit('speechcompatibility', {
                    error: this.errorMessage
                })
                return false;
            }
        },
        startSpeech: function(){
            this.checkSpeechCompatibility();
            this.isSpeaking = true;
            this.recognition.lang = this.lang;
            this.recognition.interimResults = true;

            this.recognition.addEventListener('speechstart', event => {
                this.speaking = true;
            });

            this.recognition.addEventListener('speechend', event => {
                this.speaking = false;
            });

            this.recognition.addEventListener('result', event => {
                var transcript = Array.from(event.results).map(result => result[0]).map(result => result.transcript).join('');
                this.transcript = transcript;
            });

            this.recognition.start();
        },
        stopSpeech: function(){
            this.recognition.stop();
            this.isSpeaking = false;
            this.message = this.transcript;
        },
        updateWindowSize: function(isSystem){
            timeout = isSystem?200:100;
            setTimeout(() => {
                this.messageBody.scrollTop = this.messageBody.scrollHeight + 400;
            }, timeout);
        },
        isDisabled: function(){
            if(this.form.is_round_trip === "false" || !this.form.is_round_trip){
                return true;
            }
            return false;
        },
        isNew: function(item){
            if (item === "True") {
                return true
            }
            if (item === "False") {
                return false
            }
            //return item === "True"?true:false;
        },
        isFalse: function(item){
            if (item === "True") {
                return false
            }
            if (item === "False") {
                return true
            }
        }
    },
    watch: {
        "form.is_round_trip": function(newValue, oldValue){
            this.isDisabled();
        }
    }
});