// Récupérez toutes les images de la page
var images = document.querySelectorAll('img');

// Récupérez la frame modale et le contenu de l'image dans la frame modale
var modal = document.getElementById('myModal');
var modalImg = document.getElementById("modalImg");

// Ajoutez un événement de clic à chaque image
images.forEach(function(image) {
  image.addEventListener('click', function() {
    // Affichez la frame modale
    modal.style.display = "block";
    // Affichez l'image agrandie dans la frame modale
    modalImg.src = this.src;
  });
});

// Récupérez l'élément pour fermer la frame modale
var span = document.getElementsByClassName("close")[0];

// Ajoutez un événement de clic pour fermer la frame modale lorsque l'utilisateur clique sur le bouton de fermeture
span.addEventListener('click', function() {
  modal.style.display = "none";
});


// Récupérez l'élément pour fermer la frame modale
var closeBtn = document.querySelector(".close");

// Ajoutez un événement de clic pour fermer la frame modale lorsque l'utilisateur clique sur le bouton de fermeture
closeBtn.addEventListener('click', function() {
  modal.style.display = "none";
});
