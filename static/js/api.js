/**
 * TogoBank Digital — API Client
 * Encapsule fetch() avec gestion JWT automatique.
 */
const API = {
    BASE: '/api/v1',
    token: localStorage.getItem('tb_token'),
    refreshToken: localStorage.getItem('tb_refresh'),
    user: JSON.parse(localStorage.getItem('tb_user') || 'null'),

    setAuth(data) {
        this.token = data.access_token;
        this.refreshToken = data.refresh_token;
        this.user = data.user;
        localStorage.setItem('tb_token', data.access_token);
        localStorage.setItem('tb_refresh', data.refresh_token);
        localStorage.setItem('tb_user', JSON.stringify(data.user));
    },

    clearAuth() {
        this.token = null;
        this.refreshToken = null;
        this.user = null;
        localStorage.removeItem('tb_token');
        localStorage.removeItem('tb_refresh');
        localStorage.removeItem('tb_user');
    },

    isAuthenticated() {
        return !!this.token;
    },

    async request(method, endpoint, body = null) {
        const headers = { 'Content-Type': 'application/json' };
        if (this.token) headers['Authorization'] = `Bearer ${this.token}`;

        const config = { method, headers };
        if (body) config.body = JSON.stringify(body);

        try {
            let res = await fetch(this.BASE + endpoint, config);

            // Refresh token si 401
            if (res.status === 401 && this.refreshToken) {
                const refreshRes = await fetch(this.BASE + '/auth/refresh', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.refreshToken}`
                    }
                });
                if (refreshRes.ok) {
                    const refreshData = await refreshRes.json();
                    this.token = refreshData.access_token;
                    localStorage.setItem('tb_token', this.token);
                    headers['Authorization'] = `Bearer ${this.token}`;
                    res = await fetch(this.BASE + endpoint, { method, headers, body: config.body });
                } else {
                    this.clearAuth();
                    window.location.hash = '#login';
                    return { error: 'Session expirée' };
                }
            }

            const data = await res.json();
            if (!res.ok) return { error: data.error || 'Erreur serveur', status: res.status };
            return data;
        } catch (err) {
            console.error('API Error:', err);
            return { error: 'Erreur de connexion au serveur' };
        }
    },

    get(endpoint) { return this.request('GET', endpoint); },
    post(endpoint, body) { return this.request('POST', endpoint, body); },
    patch(endpoint, body) { return this.request('PATCH', endpoint, body); },
    delete(endpoint) { return this.request('DELETE', endpoint); },
};
