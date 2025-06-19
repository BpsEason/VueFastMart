import axios from 'axios';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export async function addToCart(productId, quantity) {
  const response = await axios.post('/api/cart/', { product_id: productId, quantity }, {
    headers: getAuthHeaders()
  });
  return response.data;
}

export async function getCart() {
  const response = await axios.get('/api/cart/', {
    headers: getAuthHeaders()
  });
  return response.data;
}

export async function updateCartItem(cartItemId, productId, quantity) {
  const response = await axios.put(`/api/cart/${cartItemId}`, { product_id: productId, quantity }, {
    headers: getAuthHeaders()
  });
  return response.data;
}

export async function removeFromCart(cartItemId) {
  const response = await axios.delete(`/api/cart/${cartItemId}`, {
    headers: getAuthHeaders()
  });
  return response.data;
}