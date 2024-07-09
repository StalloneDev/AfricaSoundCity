
// Récupérer la date de l'objet prochain_concert
document.addEventListener("DOMContentLoaded", function() {
    var concertDateElement = document.getElementById("concert-date");
    if (!concertDateElement) {
        console.error("Element with ID 'concert-date' not found.");
        return;
    }

    var concertDateStr = concertDateElement.dataset.concertDate;
    if (!concertDateStr) {
        console.error("Attribute 'data-concert-date' not found or empty.");
        return;
    }
    
    // Diviser la chaîne de date en parties (jour, mois, année, heure, minute)
    if (typeof concertDateStr !== "string") {
        console.error("concertDateStr is not a string:", concertDateStr);
        return;
    } else {
        console.log(concertDateStr)
        var parts = concertDateStr.split(" ");
        console.log(parts)
        var day = parseInt(parts[0]);
        var month = parts[1];
        var year = parseInt(parts[2]);
        var time = parts[3];
        var hour = parseInt(time.split(":")[0]);
        var minute = parseInt(time.split(":")[1]);
        console.log(parts)
    }
    // Convertir le mois en son équivalent numérique
    var months = {
        "janvier": 0,
        "février": 1,
        "mars": 2,
        "avril": 3,
        "mai": 4,
        "juin": 5,
        "juillet": 6,
        "août": 7,
        "septembre": 8,
        "octobre": 9,
        "novembre": 10,
        "décembre": 11
    };
    var monthIndex = months[month.toLowerCase()];

    // Créer un objet Date avec la date et l'heure extraites
    var concertDate = new Date(year, monthIndex, day, hour, minute);

    // Vérifier si la conversion a réussi
    if (isNaN(concertDate)) {
        console.error("Erreur de conversion de la date : " + concertDateStr);
        return;
    }

    console.log(concertDate);

    // Utiliser maintenant concertDate pour votre logique de minuterie JavaScript
    var x = setInterval(function() {
        var now = new Date().getTime();
        var distance = concertDate - now;

        // Calculer les jours, heures, minutes et secondes restantes
        var days = Math.floor(distance / (1000 * 60 * 60 * 24));
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Afficher le temps restant dans les éléments avec les ID correspondants
        document.getElementById("days").innerText = days;
        document.getElementById("hours").innerText = hours;
        document.getElementById("minutes").innerText = minutes;
        document.getElementById("seconds").innerText = seconds;
        
         
        // Si la distance est inférieure à 0, l'événement est passé
        if (distance < 0) {
            clearInterval(x);
            // Afficher le temps restant dans les éléments avec les ID correspondants
            document.getElementById("days").innerText = "00";
            document.getElementById("hours").innerText = "00";
            document.getElementById("minutes").innerText = "00";
            document.getElementById("seconds").innerText = "00";
            $(".pastevent").text("L'événement est en cours ou déjà terminé !");
            // Masquer ou désactiver les boutons d'achat ici
            $(".kkiapay-button").hide();
        }
    }, 1000);
});