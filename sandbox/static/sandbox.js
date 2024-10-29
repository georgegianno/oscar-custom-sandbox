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

function disable(element) {
    element.style.pointerEvents = 'none'
    element.style.opacity= '0.5'
}

function enable(element) {
    element.style.pointerEvents = 'auto'
    element.style.opacity= '1'
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
        _updateCartInfo(lineId, quantity, data)
        _addOrRemoveGiftFromBasket(data)
        toggleGiftProgressBar(data)
    })
  
    .catch(error => {
        console.error('Error:', error)
    })
} 

function _updateCartInfo(lineId, quantity, response) {
    if (response['empty_basket'] || response['num_items']==0) {
        _emptyBasket(response)
    }
    var currency = response['currency']  
    var basketTotal = response['basket_total']
    var basketTotalInclDiscounts = response['basket_total_incl_discounts']
    var voucherKeys = Object.keys(response).filter(key => key.includes('voucher'))
    var offerKeys = Object.keys(response).filter(key => key.includes('offer'))
    var lineTotal = response['line_total'] 
    var basketLine = document.querySelector(`[data-line-id="${lineId}"]`)
    if (parseInt(quantity) > 0 && currency && lineTotal) {
        var linePrice = document.querySelector(`span[data-line-price="${lineId}"]`)
        linePrice.textContent = currency+lineTotal
    } 
    if (response['delete_line']) {
        if (basketLine) {
            basketLine.remove()
        }
    }
    if (currency) {
        if (basketTotal && basketTotalInclDiscounts) { 
            document.querySelectorAll('span[data-total="order-total"]').forEach(function(price) {
                price.textContent = currency+basketTotalInclDiscounts  
            })
            document.querySelectorAll('[data-discounts="excl"]').forEach(function(price) {
                price.textContent = currency+basketTotal 
            })
            document.querySelectorAll('[data-discounts="incl"]').forEach(function(price) {
                price.textContent = currency+basketTotalInclDiscounts  
            })
        }
        if (voucherKeys) {
            voucherKeys.forEach(function(key) {
                document.querySelector(`[data-discounts=${key}]`).textContent = '-'+currency+response[key]
            })
        }
        if (offerKeys) {
            offerKeys.forEach(function(key) {
                document.querySelector(`[data-discounts=${key}]`).textContent = '-'+currency+response[key]
            })
        }
    }
}

function _addOrRemoveGiftFromBasket(response) {
    Object.keys(response).forEach(function(key) {
        if (parseInt(key)) {
            var data = response[key]
            var canAddGiftToBasket = data['can_add_gift']
            var giftLineId = data['gift_product']
            var promoGift = document.querySelector(`.gift-product[data-promo="${key}"]`)
            if (canAddGiftToBasket==false) {
                _removeGiftFromBasket(data, key)
            } else {
                if (canAddGiftToBasket==true && giftLineId==false && !promoGift) {
                    _checkWhatGiftToAdd(key)
                }
            }
        }
    })
    if (response['empty_basket'] || response['num_items']==0) {
        _emptyBasket(response)
    }
}

async function getGiftData() {
    var csrfToken = getCsrf()
    var url = "/select_gift/"
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
    })
    const data = await response.json()
    Object.keys(data).forEach(function(key) {
        if (typeof data[key] !== undefined) {
            if (parseInt(key)) {
                var gifts = data[key]['gifts']
                if (gifts !== undefined) {
                    let currentGift
                    if (gifts && gifts !== undefined && gifts.length > 0) {
                        gifts.forEach(function(gift) {
                            if (document.querySelector(`[data-product-pk="${gift}"]`)) {
                                currentGift = gift
                            }
                        })
                    }
                    data[key]['currentGift'] = currentGift
                }
            }
        }
    })
    return data
}

function _removeGiftFromBasket(response=undefined, promo=undefined, addSelected=false, selectedGiftId=false) {
    var giftSelectionList = document.querySelector(`[data-list="gift_list_container"][data-promo="${promo}"]`)
    var giftLine = document.querySelector(`.gift-product[data-promo="${promo}"]`)
    if (giftLine) { 
        if (addSelected && selectedGiftId) {
            
            var giftLineId = giftLine.getAttribute('data-line-id')
            let csrfToken = getCsrf()
            const url = `/quantity/set/${giftLineId}/0/`
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to remove gift')
                }

                return response.json()
            })
            .then(data => {
                giftLine.remove()
                _checkWhatGiftToAdd(promo, selectedGiftId)
                setGiftList(promo, selectedGiftId)
             })
        } else {
            giftLine.remove()
            if (giftSelectionList) {
                giftSelectionList.remove()
            }
        }
    }
} 

function _checkWhatGiftToAdd(promo, selectedGift=undefined) {
    var giftSelectionList = document.querySelector(`[data-list="gift_list_container"][data-promo="${promo}"]`)
    getGiftData()
    .then(
        giftData => {
            let giftId
            var createGiftList=false
            var hideGift = false
            var gifts = giftData[promo]['gifts']
            if (selectedGift==undefined) {
                if (gifts && gifts.length > 0 && gifts !== undefined) {
                    giftId = gifts[0]
                    if (gifts.length > 1) {
                        if (!giftSelectionList) {
                            createGiftList = true
                            hideGift = true
                        }
                    }
                } 
            } else {
                giftId = selectedGift
                hideGift = true
            }
            _addGiftToBasket(promo, giftId, hideGift, createGiftList)
    })
}


function _selectNewGift(promo, giftId, hideGift, createGiftList) {
    var csrfToken = getCsrf()
    fetch('/select_gift/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,  
        },
        body: JSON.stringify({
            'gift': giftId
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok')
        }

        return response.json()
    })
    .then(data => {
        var basketLine = data['gift_line_html']
        var basketLineId = data['gift_line_id']
        var container = $('#products-info')
        var promoList = data['gift_list']
        if (basketLine && basketLineId && container && promoList) {
            container.append(basketLine)
            if (hideGift==true) {
                var lineElement = document.querySelector(`[data-line-id="${basketLineId}"]`)
                if (lineElement) {
                    lineElement.style.display = 'none'
                }
            }
            if (createGiftList==true) {
                if ($('#promo-list')) {
                    $('#promo-list').append(promoList)
                    setGiftList(promo, giftId)
                    setChangeGiftListener(promo)
                }
            }
        }
    })
    .catch(error => {
        console.error('Fetch error:', error)
    })
    .finally(() => {
        var checkoutButton = document.getElementById("checkout-button")
        var giftOptions = document.querySelectorAll('input[name="select_your_gift"]')
        var checkoutButton = document.getElementById("checkout-button")
        var giftOptions = document.querySelectorAll('input[name="select_your_gift"]')
        if (checkoutButton) {
            checkoutButton.style.pointerEvents = 'auto'
        }
        if (giftOptions) {
            giftOptions.forEach(option => {
                option.disabled = false
            })
        }
    })
}

function _addGiftToBasket(promo, giftId, hideGift, createGiftList) {
    if (promo && giftId) {
        var csrfToken = getCsrf()
        var giftUrl = '/en-gb/basket/add/' + giftId + '/'
        var giftData =
            'csrfmiddlewaretoken=' + csrfToken + '&quantity=1&child_id=' + giftId
        
        $.post(giftUrl, giftData)
        .done(function (response) {
            if (document.querySelector('.basket-mini')) {
                _updateMiniCart(response)
            } else {
                _selectNewGift(promo, giftId, hideGift, createGiftList)
            }
           
        })
        .fail(function (response) {
            console.error('Fetch error:', error)
        })
    }
}

function setGiftList(promo, giftId) {
    var giftSelectionList = document.querySelector(`[data-list="gift_list_container"][data-promo="${promo}"]`)
    if (giftSelectionList) {
        var radioToSelect = document.querySelector(`input[name="select_your_gift"][value="${giftId}"`)
        if (radioToSelect) {
            radioToSelect.checked = true
        }
        giftSelectionList.style.display = 'block'
    }
}

function setChangeGiftListener(promo) {
    var giftSelectionList = document.querySelector(`[data-list="gift_list_container"][data-promo="${promo}"]`)
    if (giftSelectionList) {
        var giftOptions = document.querySelectorAll('input[name="select_your_gift"]')
        giftOptions.forEach(option => {
            option.addEventListener('change', function(event) {
                var target = event.target
                giftOptions.forEach(option => {
                    option.disabled = true
                })
                var checkoutButton = document.getElementById("checkout-button")
                if (checkoutButton) {
                    checkoutButton.style.pointerEvents = 'none'
                }
                _removeGiftFromBasket(undefined, promo, true, target.value)
            })
        })
    }
}

function _updateMiniCart(response) {
    var miniBasketTotal = document.getElementById('mini-basket-total')
    var successMessage = response['success_message']
    var currency = response['currency']
    var basketTotal = response['basket_total']
    var quickview = response['quickview']
    var quickviewSpan = document.querySelector('span[data-quickview]')
    if (successMessage) {
        displaySuccessMessage(successMessage)
        if (miniBasketTotal && basketTotal && currency) {
            miniBasketTotal.textContent = currency+basketTotal
            miniBasketTotal.style.fontWeight = 'bold'

        }
        if (quickview && quickviewSpan) {
            quickviewSpan.innerHTML = quickview
        }
    }
}

function _addToBasket(forms) {
    forms.forEach(function(form) {
        let submitButton = form.querySelector('button[type="submit"]')
        const buttonInitialText = submitButton.textContent
        submitButton.setAttribute('data-loading-text', buttonInitialText)
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
                _updateMiniCart(data)
                submitButton.disabled = false
                submitButton.classList.remove('disabled')
                submitButton.textContent = buttonInitialText
                _addOrRemoveGiftFromBasket(data)

            })
            .catch(error => {
                console.error('Error:', error)
            })
        })
    })
}

function displayGiftSelectionLists() {
     // We fetch the gifts on page load to show progress bar or gift list
	var giftSelectionLists = document.querySelectorAll(`[data-list="gift_list_container"]`)
    giftSelectionLists.forEach(function(giftSelectionList){
        if (giftSelectionList.querySelectorAll('input[name="select_your_gift"]')) {
            getGiftData()
            .then(
                giftData => {
                    if (giftData !== undefined && typeof giftData !== undefined) {
                        Object.keys(giftData).forEach(function(key) {
                            if (parseInt(key)) {
                                var gifts = giftData[key]['gifts']
                                if (gifts && gifts.length > 1 && gifts !== undefined) {
                                    if (giftData[key]['currentGift']) {
                                        const giftId = giftData[key]['currentGift']
                                        setGiftList(key, giftId)
                                        setChangeGiftListener(key)
                                    } else {
                                        if (giftSelectionList) {
                                            giftSelectionList.remove()
                                        }
                                    }
                                }
                            }
                        })
                    }
                }
            )
        }
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

function _emptyBasket(response) {
    if (response['empty_basket']) {
        if (document.querySelector('.content')) {
            document.querySelector('.content').innerHTML = response['empty_basket']
			var giftSelectionLists = document.querySelectorAll(`[data-list="gift_list_container"]`)
            var progressBarContainer = document.getElementById('away_from_gift')
			if (progressBarContainer) {
				progressBarContainer.remove()
			}
			if (giftSelectionLists) {
				giftSelectionLists.forEach(function(list) {
					list.remove()
				})
			}
        }
    }
}

function toggleGiftProgressBar(response) {
    var progressBarContainer = document.getElementById('away_from_gift')
    Object.keys(response).forEach(function(key) {
        if (parseInt(key)) {
            const threshold = parseFloat(response[key]['gift_product_price_threshold'])
            const validTotal = parseFloat(String(response[key]['sum_of_valid_products_in_basket']).replace(',', '.')).toFixed(2)
            var remainingContainer = document.getElementById('remaining') 
            const remainingAmount = parseFloat(threshold-validTotal)
            const progressBar = document.getElementById('progress-bar')
            if (progressBar && progressBarContainer) {
                if (remainingContainer && remainingAmount && remainingAmount > 0) {
                    remainingContainer.textContent = remainingAmount.toFixed(2)
                    progressBar.value = validTotal
                    progressBar.max = String(threshold)
                    progressBarContainer.style.display = 'block';
                } else {
                    progressBarContainer.style.display = 'none';
                }
                if (!parseFloat(progressBar.value) > 0) {
                    progressBarContainer.style.display = 'none';
                }
            }
        }
    })
}

function setQuantityListeners(elements) {
    elements.forEach(function(element) {
        var input = element.querySelector('input')
        var plus = element.querySelector('[data-arrow="plus"]')
        var minus = element.querySelector('[data-arrow="minus"]')
        var max = parseInt(input.getAttribute('data-max'))
        var basketLine = input.closest('[data-line-id]')
        var lineId = basketLine.getAttribute('data-line-id')
        input.addEventListener('input', function() {
            value = parseInt(input.value)
            if (value > max) {
                input.value = max
            } else if (!(parseInt(value)) || !(0<value<=max)){
                input.value = 1
            }
            var quantity = input.value
            if (quantity && lineId) {
                _updateCartQuantity(lineId, quantity) 
            } 
        })
        plus.addEventListener('click', function() {
            var previousValue = parseInt(input.value)
            enable(minus)
            if (parseInt(input.value) == max) {
                disable(plus)
            }
            else {
                input.value = previousValue + 1
                var quantity = previousValue + 1
                if (quantity && lineId) {
                    _updateCartQuantity(lineId, quantity) 
                } 
            }
        })
        minus.addEventListener('click', function() {
            enable(plus)
            var previousValue = parseInt(input.value)
            if (previousValue > 1) {
                input.value = previousValue - 1
                var quantity = input.value
                if (quantity && lineId) {
                    _updateCartQuantity(lineId, quantity) 
                } 
            } else {
                disable(minus)
            }
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

document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('keydown', function(event) {
        if (event.key=='Enter') {
            event.preventDefault()
        }
    })
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
        addOrRemoveFavorites(favoriteLinks)
    }
    displayGiftSelectionLists()
})

