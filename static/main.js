const buttons = document.querySelectorAll('#checkout');
const hearts = document.querySelectorAll("#heart")

buttons.forEach(button =>{
    button.addEventListener('click', event => {
        fetch('/stripe_pay')
        .then((result) => { return result.json(); })
        .then((data) => {
            var stripe = Stripe(data.checkout_public_key);
            stripe.redirectToCheckout({
                sessionId: data.checkout_session_id
            }).then(function (result) {
            });
        })
    });
})

hearts.forEach(heart =>{
    heart.addEventListener('click', (e) => {
        if(heart.classList.contains("text-danger")){
            heart.classList = "bi bi-heart"
        }
        else{
            heart.classList = "bi bi-heart-fill text-danger"
        }
    })
})