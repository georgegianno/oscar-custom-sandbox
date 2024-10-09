document.addEventListener('DOMContentLoaded', function() {
    var quantityInputs = document.querySelectorAll('.input-group')
    if (quantityInputs) {
        setQuantityListeners(quantityInputs)
    }
    var removeLinks = document.querySelectorAll('a[data-action="remove"]')
    if (removeLinks) {
        setRemoveListeners(removeLinks)
    }
    var basketAddForms = document.querySelectorAll('form[action*="/basket/add/"]')
    if (basketAddForms) {
        _addToBasket(basketAddForms)
    }
    var favoriteLinks = document.querySelectorAll('a[data-favorite-product]')
    if (favoriteLinks) {
        console.log(favoriteLinks)
        addOrRemoveFavorites(favoriteLinks)
    }
})

function getCsrf() {
    let csrfToken = null
    const cookies = document.cookie.split('; ')
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].split('=')
        if (cookie[0] === 'csrftoken') {
            csrfToken = cookie[1]
            break
        }
    }
    return csrfToken
}

function _updateCart(event) {
    var quantity = event.target.value
    if (parseInt(quantity) > parseInt(event.target.max)) {
        event.target.value = event.target.max
        quantity = event.target.max
    }
    if (parseInt(quantity) < 0) {
        event.target.value = 1
        quantity = 1
    }
    var basketLine = event.target.closest('[data-line-id]')
    var lineId = basketLine.getAttribute('data-line-id')
    if (quantity && lineId) {
        _updateCartQuantity(lineId, quantity) 
    } 
}

function _updateCartQuantity(lineId, quantity) {
    let csrfToken = getCsrf()
    const url = `/quantity/set/${lineId}/${quantity}/`
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
    })
    .then(response => {
        if (response.ok) {
            return response.json()
        } else {
            throw new Error('Failed to update quantity')
        }
    })
    .then(data => {
        if (data['empty_basket']) {
            _emptyBasket(data)
        }
        var currency = data['currency']  
        var basketTotal = data['basket_total']
        var lineTotal = data['line_total'] 
        var basketLine = document.querySelector(`[data-line-id="${lineId}"]`)
        if (parseInt(quantity) > 0 && currency && lineTotal) {
            var linePrice = document.querySelector(`span[data-line-price="${lineId}"]`)
            linePrice.textContent = currency+lineTotal
        } 
        if (data['delete_line']) {
            if (basketLine) {
                basketLine.remove()
            }
        }
        if (currency && basketTotal) {
            document.querySelectorAll('span[data-total="order-total"]').forEach(function(price) {
                price.textContent = currency+basketTotal  
            })
        }
    })
    .catch(error => {
        console.error('Error:', error)
    })
} 

function _addToBasket(forms) {
    forms.forEach(function(form) {
        let submitButton = form.querySelector('button[type="submit"]')
        const buttonInitialText = submitButton.textContent
        submitButton.setAttribute('data-loading-text', buttonInitialText)
        var miniBasketTotal = document.getElementById('mini-basket-total')
        form.addEventListener('submit', function(event) {
            event.preventDefault()
            let csrfToken = getCsrf()
            let formData = new FormData(form)
            formData.append('csrfmiddlewaretoken', csrfToken)
            formData.append('quantity', 1)
            fetch(form.action, {
                method: 'POST',
                body: formData, 
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was:' + response.statusText)
                }
                return response.json()
            })
            .then(data => {
                var successMessage = data['success_message']
                var currency = data['currency']
                var basketTotal = data['basket_total']
                var quickview = data['quickview']
                var quickviewSpan = document.querySelector('span[data-quickview]')
                console.log(quickview)
                if (successMessage) {
                    displaySuccessMessage(successMessage)
                    submitButton.disabled = false
                    submitButton.classList.remove('disabled')
                    submitButton.textContent = buttonInitialText
                    if (miniBasketTotal && basketTotal && currency) {
                        miniBasketTotal.textContent = currency+basketTotal
                    }
                    if (quickview && quickviewSpan) {
                        quickviewSpan.innerHTML = quickview
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error)
            })
        })
    })
}

function displaySuccessMessage(message) {
    const successMessageContainer = document.createElement('div')
    successMessageContainer.innerHTML = message
    document.body.appendChild(successMessageContainer) 
    successMessageContainer.style.position = 'fixed' 
    successMessageContainer.style.top = '50%' 
    successMessageContainer.style.left = '50%' 
    successMessageContainer.style.transform = 'translate(-50%, -50%)' 
    successMessageContainer.style.backgroundColor = 'rgba(var(--bs-emphasis-color-rgb), 0.85)'
    successMessageContainer.style.color = 'white'
    successMessageContainer.style.padding = '60px'
    successMessageContainer.style.borderRadius = '5px'
    successMessageContainer.style.zIndex = '1000' 
    successMessageContainer.style.textAlign = 'center' 
    successMessageContainer.style.fontSize = '25px' 
    setTimeout(() => {
        document.body.removeChild(successMessageContainer)
    }, 1200) 
}

function setQuantityListeners(elements) {
    elements.forEach(function(element) {
        var input = element.querySelector('input')
        input.addEventListener('input', (event) => {
            _updateCart(event)

        })
        element.addEventListener('click', function(event) {
            _updateCart(event)
        })
    })
}

function setRemoveListeners(elements) {
    elements.forEach(function(element) {
        element.addEventListener('click', function(event) {
            event.preventDefault()
            var basketLine = element.closest('[data-line-id]')
            var lineId = basketLine.getAttribute('data-line-id')
            if (basketLine && lineId) {
                _updateCartQuantity(lineId, 0) 
            } 
        })
    })
}

function addOrRemoveFavorites(links) {
    links.forEach(function(link) {
        link.addEventListener('click', function(event) {
            event.preventDefault()
            var csrfToken = getCsrf()
            url = link.href
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was:' + response.statusText)
                }
                return response.json()
            })
            .then(data => {
                console.log(data)
                var successMessage = data['success_message']
                var displayText = data['display_text']
                if (successMessage) {
                    displaySuccessMessage(successMessage)
                if (displayText) {
                    link.textContent = displayText 
                }
                }
            })
            .catch(error => {
                console.error('Error:', error)
            })
        })
    })
}

function _emptyBasket(response) {
    if (response['empty_basket']) {
        if (document.querySelector('.content')) {
            document.querySelector('.content').innerHTML = response['empty_basket']
        }
    }
}

