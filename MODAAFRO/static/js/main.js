// static/js/main.js (VERSÃO BOOTSTRAP)

document.addEventListener('DOMContentLoaded', () => {

    // --- VARIÁVEIS GLOBAIS ---
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    const cartIcon = document.getElementById('cart-icon');
    const whatsappCheckoutButton = document.getElementById('whatsapp-checkout-btn');
    const whatsappNumber = document.body.dataset.whatsappNumber;

    // --- INICIALIZAÇÃO DOS MODAIS BOOTSTRAP ---
    // Pegamos os elementos HTML dos modais
    const cartModalEl = document.getElementById('cart-modal');
    const productModalEl = document.getElementById('product-modal');

    // Verificamos se eles existem antes de criar as instâncias
    let cartModalBS = null;
    let productModalBS = null;

    if (cartModalEl) {
        cartModalBS = new bootstrap.Modal(cartModalEl);
    }
    if (productModalEl) {
        productModalBS = new bootstrap.Modal(productModalEl);
    }
    
    // --- FUNÇÕES DO CARRINHO (Sem grandes mudanças) ---

    function addToCart(id, nome, preco, imagem) {
        const existingItem = cart.find(item => item.id === id);
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.push({ id, nome, preco, imagem, quantity: 1 });
        }
        saveCart();
        updateCartUI();
        showCartModal(); // Abre o modal do carrinho
    }

    function saveCart() {
        localStorage.setItem('cart', JSON.stringify(cart));
    }

    function updateCartUI() {
        if (!cartIcon || !cartModalEl) return; // Segurança

        // Atualiza o contador do ícone
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        const cartCountEl = cartIcon.querySelector('.cart-count');
        if (cartCountEl) {
            cartCountEl.textContent = totalItems;
            cartCountEl.style.display = totalItems > 0 ? 'block' : 'none';
        }

        // Atualiza o conteúdo do modal do carrinho
        const cartItemsContainer = cartModalEl.querySelector('.cart-items');
        const cartTotalEl = cartModalEl.querySelector('.cart-total');
        
        cartItemsContainer.innerHTML = '';
        let totalGeral = 0;

        if (cart.length === 0) {
            cartItemsContainer.innerHTML = '<p class="text-center text-secondary">Seu carrinho está vazio.</p>';
            whatsappCheckoutButton.disabled = true;
        } else {
            cart.forEach(item => {
                if (!item || typeof item.preco === 'undefined' || item.preco === null) {
                    console.error('Item inválido no carrinho:', item);
                    return; 
                }
                const precoNum = parseFloat(item.preco);
                const itemTotal = precoNum * item.quantity;
                totalGeral += itemTotal;
                
                // HTML do item do carrinho (um pouco de Bootstrap)
                cartItemsContainer.innerHTML += `
                    <div class="cart-item d-flex align-items-center justify-content-between gap-3 mb-3 border-bottom pb-3">
                        <img src="${item.imagem}" alt="${item.nome}" style="width: 60px; height: 60px; object-fit: cover;" class="rounded">
                        <div class="flex-grow-1">
                            <strong class="d-block">${item.nome}</strong>
                            <span class="text-secondary">${item.quantity} x R$ ${precoNum.toFixed(2)}</span>
                        </div>
                        <strong class="text-nowrap">R$ ${itemTotal.toFixed(2)}</strong>
                        <button class="btn btn-sm btn-outline-danger remove-from-cart" data-id="${item.id}">&times;</button>
                    </div>
                `;
            });
            whatsappCheckoutButton.disabled = false;
        }
        
        cartTotalEl.textContent = `Total: R$ ${totalGeral.toFixed(2)}`;
    }

    function removeFromCart(id) {
        cart = cart.filter(item => item.id !== id);
        saveCart();
        updateCartUI();
    }

    function clearCart() {
        cart = [];
        saveCart();
        updateCartUI();
    }

    // --- FUNÇÕES DE MODAL (Atualizadas para Bootstrap) ---

    function showCartModal() {
        if (cartModalBS) {
            cartModalBS.show();
        }
    }

    function closeCartModal() {
        if (cartModalBS) {
            cartModalBS.hide();
        }
    }

    async function showProductModal(productId) {
        if (!productModalBS) return; // Se o modal não existe, sai da função

        try {
            const response = await fetch(`/produto/${productId}`);
            if (!response.ok) throw new Error('Produto não encontrado');
            
            const produto = await response.json();
            
            // Popula o modal do produto (usando as classes que definimos no layout)
            const modal = productModalEl;
            modal.querySelector('.product-modal-title').textContent = produto.nome;
            modal.querySelector('.product-modal-price').textContent = `R$ ${produto.preco}`;
            modal.querySelector('.product-modal-description').textContent = produto.descricao;
            
            const destaqueImg = modal.querySelector('.product-modal-main-image img');
            destaqueImg.src = produto.imagem_destaque;
            destaqueImg.alt = produto.nome;

            const gallery = modal.querySelector('.product-modal-gallery');
            gallery.innerHTML = '';
            
            const allImages = [produto.imagem_destaque, ...produto.imagens.filter(img => img !== produto.imagem_destaque)];
            
            allImages.forEach((imgUrl, index) => {
                if (imgUrl) { // Garante que a URL não é nula
                    gallery.innerHTML += `
                        <img src="${imgUrl}" alt="${produto.nome}" 
                             style="width: 80px; height: 80px; object-fit: cover; cursor: pointer;" 
                             class="rounded border ${index === 0 ? 'border-primary border-2' : ''}">
                    `;
                }
            });

            const addToCartBtn = modal.querySelector('.add-to-cart-modal-btn');
            addToCartBtn.replaceWith(addToCartBtn.cloneNode(true)); // Limpa listeners antigos
            
            modal.querySelector('.add-to-cart-modal-btn').addEventListener('click', () => {
                addToCart(produto.id, produto.nome, parseFloat(produto.preco), produto.imagem_destaque);
                closeProductModal();
            });

            productModalBS.show(); // MOSTRA O MODAL (API do Bootstrap)

        } catch (error) {
            console.error('Erro ao buscar produto:', error);
            alert('Não foi possível carregar os detalhes do produto.');
        }
    }

    function closeProductModal() {
        if (productModalBS) {
            productModalBS.hide(); // ESCONDE O MODAL (API do Bootstrap)
        }
    }
    
    // --- CHECKOUT WHATSAPP (Sem mudanças) ---

    function handleWhatsAppCheckout() {
        if (cart.length === 0) return;
        let mensagem = "Olá! Gostaria de fazer o seguinte pedido:\n\n";
        let totalGeral = 0;
        cart.forEach(item => {
            const itemTotal = parseFloat(item.preco) * item.quantity;
            totalGeral += itemTotal;
            mensagem += `*Produto:* ${item.nome}\n`;
            mensagem += `*Quantidade:* ${item.quantity}\n`;
            mensagem += `*Subtotal:* R$ ${itemTotal.toFixed(2)}\n`;
            mensagem += "--------------------\n";
        });
        mensagem += `\n*TOTAL DO PEDIDO: R$ ${totalGeral.toFixed(2)}*`;
        const encodedMessage = encodeURIComponent(mensagem);
        const whatsappURL = `https://wa.me/${whatsappNumber}?text=${encodedMessage}`;
        window.open(whatsappURL, '_blank');
    }

    // --- EVENT LISTENERS (Delegação de Eventos) ---

    // Não precisamos mais do listener de fechar modal (data-bs-dismiss faz isso)
    
    document.body.addEventListener('click', (e) => {
        
        // Abrir modal do produto (clicando no card)
        // A classe 'product-card' será substituída por 'card' e 'product-card-link'
        const productCard = e.target.closest('.product-card-link');
        if (productCard) {
            e.preventDefault();
            const id = productCard.dataset.productId;
            showProductModal(id);
        }

        // Clicar em um banner que linka para um produto
        const bannerLink = e.target.closest('a[href^="#product-modal-trigger-"]');
        if (bannerLink) {
            e.preventDefault(); 
            const href = bannerLink.getAttribute('href');
            const productId = href.split('-').pop(); 
            if (productId) {
                showProductModal(parseInt(productId));
            }
        }

        // Abrir modal do carrinho
        if (e.target.closest('#cart-icon')) {
            showCartModal();
        }
        
        // Remover item do carrinho
        if (e.target.classList.contains('remove-from-cart')) {
            const id = parseInt(e.target.dataset.id);
            removeFromCart(id);
        }
        
        // Checkout WhatsApp
        if (e.target.id === 'whatsapp-checkout-btn') {
            handleWhatsAppCheckout();
        }

        // Troca de imagem na galeria do modal de produto
        const galleryImg = e.target.closest('.product-modal-gallery img');
        if(galleryImg) {
            const gallery = galleryImg.closest('.product-modal-gallery');
            const mainImage = productModalEl.querySelector('.product-modal-main-image img');
            
            gallery.querySelectorAll('img').forEach(img => img.classList.remove('border-primary', 'border-2'));
            galleryImg.classList.add('border-primary', 'border-2');
            mainImage.src = galleryImg.src;
        }
    });

    // --- INICIALIZAÇÃO ---
    updateCartUI(); // Atualiza o carrinho ao carregar a página
});