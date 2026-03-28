/**
 * TogoBank Digital — Main Application
 * Routeur SPA, rendu des pages, composants.
 */
const App = {
    currentPage: null,
    charts: {},

    /** Initialisation */
    init() {
        this.initTheme();
        this.initRouter();
        this.initMobileMenu();
        this.initModal();
    },

    /* ========== THEME ========== */
    initTheme() {
        const t = localStorage.getItem('togobank-theme') || 'light';
        document.documentElement.setAttribute('data-theme', t);
        this.updateThemeIcon();
        document.getElementById('themeToggle')?.addEventListener('click', () => {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            document.documentElement.setAttribute('data-theme', isDark ? 'light' : 'dark');
            localStorage.setItem('togobank-theme', isDark ? 'light' : 'dark');
            this.updateThemeIcon();
        });
    },
    updateThemeIcon() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        document.querySelectorAll('.theme-toggle i').forEach(i => i.className = isDark ? 'fas fa-sun' : 'fas fa-moon');
    },

    /* ========== ROUTER ========== */
    initRouter() {
        window.addEventListener('hashchange', () => this.route());
        this.route();
    },
    route() {
        const hash = (location.hash || '#login').replace('#', '');
        const authPages = ['login', 'register', 'forgot-password'];

        if (authPages.includes(hash)) {
            document.getElementById('authView').style.display = '';
            document.getElementById('appView').style.display = 'none';
            const authCard = document.getElementById('authCard');
            authCard.innerHTML = hash === 'register' ? Auth.renderRegister() : Auth.renderLogin();
            authCard.classList.remove('animate-scale-in');
            void authCard.offsetWidth;
            authCard.classList.add('animate-scale-in');
            Auth.currentStep = 1;
            Auth.init();
            return;
        }

        if (!API.isAuthenticated()) {
            location.hash = '#login';
            return;
        }

        document.getElementById('authView').style.display = 'none';
        document.getElementById('appView').style.display = '';
        this.updateSidebar();
        this.renderPage(hash || 'dashboard');
    },

    updateSidebar() {
        const u = API.user;
        if (!u) return;
        document.getElementById('sidebarAvatar').textContent = (u.prenom?.[0] || '') + (u.nom?.[0] || '');
        document.getElementById('sidebarUserName').textContent = `${u.prenom} ${u.nom}`;
        document.getElementById('sidebarUserRole').textContent = u.role === 'super_admin' ? 'Super Admin' : u.role === 'admin' ? 'Admin' : 'Client';
        document.getElementById('pageSubtitle').textContent = `Bienvenue, ${u.prenom}`;
        if (['admin', 'super_admin'].includes(u.role)) {
            document.getElementById('adminNavSection').style.display = '';
        }
        // Active nav
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        document.querySelectorAll('.bottom-nav-item').forEach(n => n.classList.remove('active'));
        const hash = location.hash.replace('#', '') || 'dashboard';
        document.querySelector(`.nav-item[data-page="${hash}"]`)?.classList.add('active');
        document.querySelector(`.bottom-nav-item[data-page="${hash}"]`)?.classList.add('active');
        // Logout
        document.getElementById('logoutBtn').onclick = () => {
            API.clearAuth();
            location.hash = '#login';
            this.toast('Déconnexion réussie', 'success');
        };
    },

    async renderPage(page) {
        this.currentPage = page;
        const el = document.getElementById('pageContent');
        const titles = {
            dashboard: ['Tableau de bord', 'Vue d\'ensemble de vos finances'],
            accounts: ['Mes Comptes', 'Gérez vos comptes bancaires'],
            transactions: ['Transactions', 'Historique de vos opérations'],
            transfer: ['Virement', 'Envoyez de l\'argent'],
            topup: ['Recharge Mobile', 'Rechargez via Mixx By Yas ou Flooz'],
            card: ['Ma Carte', 'Carte bancaire virtuelle'],
            beneficiaries: ['Bénéficiaires', 'Gérez vos contacts'],
            savings: ['Épargne', 'Objectifs et comptes épargne'],
            notifications: ['Notifications', 'Centre de notifications'],
            profile: ['Mon Profil', 'Informations personnelles'],
            security: ['Sécurité', 'Paramètres de sécurité'],
            admin: ['Administration', 'Panneau d\'administration'],
        };
        const [title, sub] = titles[page] || [page, ''];
        document.getElementById('pageTitle').textContent = title;
        document.getElementById('pageSubtitle').textContent = sub;

        // Show skeleton
        el.innerHTML = '<div class="grid grid-3"><div class="skeleton skeleton-card"></div><div class="skeleton skeleton-card"></div><div class="skeleton skeleton-card"></div></div>';

        // Render page
        const renderer = this.pages[page];
        if (renderer) {
            await renderer.call(this, el);
        } else {
            el.innerHTML = `<div class="empty-state"><div class="empty-state-icon"><i class="fas fa-hard-hat"></i></div><div class="empty-state-title">Page en construction</div><p>Cette section sera bientôt disponible.</p></div>`;
        }

        // Animate children
        el.querySelectorAll('.stagger-item').forEach((item, i) => {
            setTimeout(() => item.classList.add('visible'), i * 80);
        });
    },

    /* ========== PAGES ========== */
    pages: {
        async dashboard(el) {
            const [accts, stats] = await Promise.all([
                API.get('/accounts'),
                API.get('/transactions/stats')
            ]);
            if (accts.error || stats.error) {
                el.innerHTML = `<div class="empty-state"><p>${accts.error || stats.error}</p></div>`;
                return;
            }

            const totalSolde = accts.total_solde || 0;
            const comptes = accts.comptes || [];
            const txRecentes = stats.transactions_recentes || [];
            const totalCredits = stats.total_credits || 0;
            const totalDebits = stats.total_debits || 0;

            el.innerHTML = `
            <div class="grid grid-4 stagger-item" id="statsRow">
                <div class="card stat-card">
                    <div class="stat-icon blue"><i class="fas fa-wallet"></i></div>
                    <div><div class="stat-value font-mono" data-count="${totalSolde}">${App.formatMoney(totalSolde)}</div><div class="stat-label">Solde total</div></div>
                </div>
                <div class="card stat-card">
                    <div class="stat-icon green"><i class="fas fa-arrow-down"></i></div>
                    <div><div class="stat-value font-mono">${App.formatMoney(totalCredits)}</div><div class="stat-label">Crédits (30j)</div></div>
                </div>
                <div class="card stat-card">
                    <div class="stat-icon red"><i class="fas fa-arrow-up"></i></div>
                    <div><div class="stat-value font-mono">${App.formatMoney(totalDebits)}</div><div class="stat-label">Débits (30j)</div></div>
                </div>
                <div class="card stat-card">
                    <div class="stat-icon gold"><i class="fas fa-exchange-alt"></i></div>
                    <div><div class="stat-value">${stats.nb_transactions || 0}</div><div class="stat-label">Transactions</div></div>
                </div>
            </div>

            <div class="grid grid-2" style="margin-top:var(--space-6)">
                <div class="card stagger-item">
                    <div class="card-header"><h3 class="card-title">Évolution du solde</h3></div>
                    <div class="chart-container"><canvas id="balanceChart"></canvas></div>
                </div>
                <div class="card stagger-item">
                    <div class="card-header"><h3 class="card-title">Entrées / Sorties</h3></div>
                    <div class="chart-container"><canvas id="flowChart"></canvas></div>
                </div>
            </div>

            <div class="grid grid-2" style="margin-top:var(--space-6)">
                <div class="card stagger-item">
                    <div class="card-header">
                        <h3 class="card-title">Comptes</h3>
                        <a href="#accounts" class="btn btn-secondary btn-sm">Voir tout</a>
                    </div>
                    ${comptes.map(c => `
                        <div style="display:flex;justify-content:space-between;align-items:center;padding:var(--space-3) 0;border-bottom:1px solid var(--border-light)">
                            <div>
                                <div style="font-weight:600;font-size:var(--text-sm)">${c.libelle}</div>
                                <div style="font-size:var(--text-xs);color:var(--text-tertiary)">${c.numero_compte}</div>
                            </div>
                            <div style="text-align:right">
                                <div class="font-mono" style="font-weight:700">${App.formatMoney(c.solde)}</div>
                                <span class="badge badge-${c.statut === 'actif' ? 'success' : 'warning'}">${c.statut}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="card stagger-item">
                    <div class="card-header">
                        <h3 class="card-title">Transactions récentes</h3>
                        <a href="#transactions" class="btn btn-secondary btn-sm">Voir tout</a>
                    </div>
                    ${txRecentes.length === 0 ? '<div class="empty-state"><p>Aucune transaction</p></div>' :
                    txRecentes.slice(0, 5).map(t => `
                        <div style="display:flex;align-items:center;gap:var(--space-3);padding:var(--space-3) 0;border-bottom:1px solid var(--border-light)">
                            <div class="avatar" style="width:36px;height:36px;font-size:0.8rem;background:${t.direction === 'credit' ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)'};color:${t.direction === 'credit' ? 'var(--success)' : 'var(--danger)'}">
                                <i class="fas fa-arrow-${t.direction === 'credit' ? 'down' : 'up'}"></i>
                            </div>
                            <div style="flex:1;min-width:0">
                                <div style="font-weight:600;font-size:var(--text-sm);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${t.description || t.type_transaction}</div>
                                <div style="font-size:var(--text-xs);color:var(--text-tertiary)">${App.formatDate(t.created_at)}</div>
                            </div>
                            <div class="font-mono" style="font-weight:700;color:${t.direction === 'credit' ? 'var(--success)' : 'var(--danger)'}">
                                ${t.direction === 'credit' ? '+' : '-'}${App.formatMoney(t.montant)}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div style="margin-top:var(--space-6);display:flex;gap:var(--space-3);flex-wrap:wrap" class="stagger-item">
                <a href="#transfer" class="btn btn-primary"><i class="fas fa-paper-plane"></i> Virer</a>
                <a href="#topup" class="btn btn-gold"><i class="fas fa-mobile-screen-button"></i> Recharger</a>
                <a href="#card" class="btn btn-secondary"><i class="fas fa-credit-card"></i> Ma Carte</a>
                <a href="#savings" class="btn btn-secondary"><i class="fas fa-piggy-bank"></i> Épargner</a>
            </div>
            `;

            // Charts
            setTimeout(() => App.initDashboardCharts(txRecentes, totalCredits, totalDebits), 100);
        },

        async accounts(el) {
            const data = await API.get('/accounts');
            if (data.error) { el.innerHTML = `<div class="empty-state"><p>${data.error}</p></div>`; return; }
            const comptes = data.comptes || [];
            el.innerHTML = `
            <div style="display:flex;justify-content:flex-end;margin-bottom:var(--space-6)">
                <button class="btn btn-primary" onclick="App.openNewAccount()"><i class="fas fa-plus"></i> Nouveau compte</button>
            </div>
            <div class="grid grid-2">
                ${comptes.map(c => `
                <div class="card stagger-item" style="cursor:pointer" onclick="location.hash='#accounts/${c.id}'">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:var(--space-4)">
                        <div>
                            <span class="badge badge-blue">${c.type_compte}</span>
                            <h3 style="font-size:var(--text-lg);margin-top:var(--space-2)">${c.libelle}</h3>
                            <div class="font-mono" style="font-size:var(--text-xs);color:var(--text-tertiary)">${c.numero_compte}</div>
                        </div>
                        <span class="badge badge-${c.statut === 'actif' ? 'success' : 'danger'}">${c.statut}</span>
                    </div>
                    <div class="font-display" style="font-size:var(--text-3xl);font-weight:700;margin-bottom:var(--space-2)">
                        ${App.formatMoney(c.solde)}
                    </div>
                    <div style="font-size:var(--text-xs);color:var(--text-tertiary)">
                        Disponible : ${App.formatMoney(c.solde_disponible)} · Devise : ${c.devise}
                    </div>
                    <div class="divider"></div>
                    <div style="display:flex;gap:var(--space-2)">
                        <a href="#transfer" class="btn btn-sm btn-secondary"><i class="fas fa-paper-plane"></i> Virer</a>
                        <a href="#topup" class="btn btn-sm btn-secondary"><i class="fas fa-mobile-screen-button"></i> Recharger</a>
                    </div>
                </div>
                `).join('')}
            </div>`;
        },

        async transactions(el) {
            const data = await API.get('/transactions?per_page=30');
            if (data.error) { el.innerHTML = `<p>${data.error}</p>`; return; }
            const txs = data.transactions || [];
            el.innerHTML = `
            <div class="card stagger-item">
                <div style="display:flex;gap:var(--space-3);margin-bottom:var(--space-4);flex-wrap:wrap">
                    <input type="text" class="form-input" placeholder="Rechercher..." style="max-width:300px" id="txSearch">
                    <select class="form-input form-select" style="max-width:180px" id="txFilter">
                        <option value="">Tous les types</option>
                        <option value="virement">Virements</option>
                        <option value="recharge">Recharges</option>
                        <option value="frais">Frais</option>
                    </select>
                </div>
                <div class="table-wrapper">
                    <table class="data-table" id="txTable">
                        <thead><tr>
                            <th>Date</th><th>Description</th><th>Référence</th><th>Type</th><th>Statut</th><th style="text-align:right">Montant</th>
                        </tr></thead>
                        <tbody>
                        ${txs.map(t => `
                            <tr>
                                <td>${App.formatDate(t.created_at)}</td>
                                <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${t.description || '—'}</td>
                                <td><span class="font-mono" style="font-size:var(--text-xs)">${t.reference}</span></td>
                                <td><span class="badge badge-blue">${t.type_transaction}</span></td>
                                <td><span class="badge badge-${t.statut === 'valide' ? 'success' : t.statut === 'echoue' ? 'danger' : 'warning'}">${t.statut}</span></td>
                                <td style="text-align:right;font-weight:700" class="font-mono">
                                    <span style="color:${t.direction === 'credit' ? 'var(--success)' : 'var(--danger)'}">
                                        ${t.direction === 'credit' ? '+' : '-'}${App.formatMoney(t.montant)}
                                    </span>
                                </td>
                            </tr>
                        `).join('')}
                        </tbody>
                    </table>
                </div>
                ${txs.length === 0 ? '<div class="empty-state"><div class="empty-state-icon"><i class="fas fa-receipt"></i></div><p>Aucune transaction</p></div>' : ''}
            </div>`;
        },

        async transfer(el) {
            const data = await API.get('/accounts');
            const comptes = data.comptes || [];
            el.innerHTML = `
            <div style="max-width:560px;margin:0 auto">
                <div class="card stagger-item">
                    <h3 class="card-title" style="margin-bottom:var(--space-6)"><i class="fas fa-paper-plane" style="color:var(--accent-blue)"></i> Effectuer un virement</h3>
                    <form id="transferForm">
                        <div class="form-group">
                            <label class="form-label">Compte source</label>
                            <select class="form-input form-select" id="trSource" required>
                                ${comptes.filter(c => c.statut === 'actif').map(c => `<option value="${c.id}">${c.libelle} — ${App.formatMoney(c.solde)}</option>`).join('')}
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Destinataire (n° de compte ou téléphone)</label>
                            <input type="text" class="form-input" id="trDest" placeholder="TG00... ou 9XXXXXXX" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Montant (FCFA)</label>
                            <input type="number" class="form-input" id="trAmount" placeholder="10 000" min="100" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Motif (optionnel)</label>
                            <input type="text" class="form-input" id="trMotif" placeholder="Ex: Loyer mars 2025">
                        </div>
                        <div id="trSummary" style="display:none;margin-bottom:var(--space-4)">
                            <div class="card" style="background:var(--bg-tertiary);padding:var(--space-4)">
                                <div style="font-size:var(--text-sm);color:var(--text-secondary)">Récapitulatif</div>
                                <div id="trSumContent"></div>
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary btn-block btn-lg" id="trBtn">
                            <i class="fas fa-paper-plane"></i> Envoyer le virement
                        </button>
                    </form>
                </div>
            </div>`;

            document.getElementById('transferForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const btn = document.getElementById('trBtn');
                btn.disabled = true;
                btn.innerHTML = '<div class="loader-spinner" style="width:20px;height:20px;border-width:2px"></div> Traitement...';
                const res = await API.post('/transactions/transfer', {
                    compte_source_id: document.getElementById('trSource').value,
                    dest_identifier: document.getElementById('trDest').value,
                    montant: parseFloat(document.getElementById('trAmount').value),
                    motif: document.getElementById('trMotif').value,
                });
                if (res.error) {
                    App.toast(res.error, 'error');
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-paper-plane"></i> Envoyer le virement';
                    return;
                }
                App.toast(res.message, 'success');
                location.hash = '#dashboard';
            });
        },

        async topup(el) {
            const data = await API.get('/accounts');
            const comptes = data.comptes || [];
            el.innerHTML = `
            <div style="max-width:560px;margin:0 auto">
                <div class="tabs" id="topupTabs">
                    <button class="tab-btn active" data-op="mixx" onclick="App.switchTopupTab('mixx')">
                        <i class="fas fa-signal"></i> Mixx By Yas
                    </button>
                    <button class="tab-btn" data-op="flooz" onclick="App.switchTopupTab('flooz')">
                        <i class="fas fa-mobile-screen-button"></i> Flooz
                    </button>
                </div>
                <div class="card stagger-item">
                    <form id="topupForm">
                        <div class="form-group">
                            <label class="form-label">Compte à créditer</label>
                            <select class="form-input form-select" id="topupCompte" required>
                                ${comptes.filter(c=>c.statut==='actif').map(c=>`<option value="${c.id}">${c.libelle} — ${App.formatMoney(c.solde)}</option>`).join('')}
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label" id="topupPhoneLabel">Numéro Yas Togo (9XXXXXXX)</label>
                            <input type="tel" class="form-input" id="topupPhone" placeholder="9XXXXXXX" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Montant (FCFA)</label>
                            <input type="number" class="form-input" id="topupAmount" min="500" max="200000" placeholder="5 000" required>
                            <div style="font-size:var(--text-xs);color:var(--text-tertiary);margin-top:4px" id="topupLimits">Min: 500 · Max: 200 000 FCFA</div>
                        </div>
                        <button type="submit" class="btn btn-gold btn-block btn-lg" id="topupBtn">
                            <i class="fas fa-mobile-screen-button"></i> Initier la recharge
                        </button>
                    </form>
                    <div id="topupResult" style="display:none;margin-top:var(--space-6)"></div>
                </div>
            </div>`;

            let currentOp = 'mixx';
            document.getElementById('topupForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const btn = document.getElementById('topupBtn');
                btn.disabled = true;
                btn.innerHTML = '<div class="loader-orbital"></div>';
                const res = await API.post(`/topup/${currentOp}/initiate`, {
                    compte_id: document.getElementById('topupCompte').value,
                    numero_tel: document.getElementById('topupPhone').value,
                    montant: parseFloat(document.getElementById('topupAmount').value),
                });
                if (res.error) {
                    App.toast(res.error, 'error');
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-mobile-screen-button"></i> Initier la recharge';
                    return;
                }
                // Mock: auto-confirm
                const confRes = await API.post(`/topup/confirm/${res.recharge.id}`, {});
                if (confRes.error) {
                    App.toast(confRes.error, 'error');
                } else {
                    App.toast(confRes.message, 'success');
                    document.getElementById('topupResult').style.display = '';
                    document.getElementById('topupResult').innerHTML = `
                        <div style="text-align:center;padding:var(--space-6)">
                            <div style="font-size:3rem;color:var(--success);margin-bottom:var(--space-3)">
                                <i class="fas fa-check-circle"></i>
                            </div>
                            <h3>Recharge réussie !</h3>
                            <p style="color:var(--text-secondary);margin:var(--space-2) 0">${App.formatMoney(res.recharge.montant)} crédités sur votre compte</p>
                            <p class="font-mono" style="font-size:var(--text-xs);color:var(--text-tertiary)">Réf: ${res.recharge.reference_interne}</p>
                            <a href="#dashboard" class="btn btn-primary" style="margin-top:var(--space-4)">Retour au tableau de bord</a>
                        </div>
                    `;
                }
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-mobile-screen-button"></i> Initier la recharge';
            });

            App.switchTopupTab = function(op) {
                currentOp = op;
                document.querySelectorAll('#topupTabs .tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelector(`#topupTabs .tab-btn[data-op="${op}"]`).classList.add('active');
                if (op === 'mixx') {
                    document.getElementById('topupPhoneLabel').textContent = 'Numéro Moov (9XXXXXXX)';
                    document.getElementById('topupPhone').placeholder = '9XXXXXXX';
                    document.getElementById('topupLimits').textContent = 'Min: 500 · Max: 200 000 FCFA';
                    document.getElementById('topupAmount').max = 200000;
                } else {
                    document.getElementById('topupPhoneLabel').textContent = 'Numéro Togocom (7/8XXXXXXX)';
                    document.getElementById('topupPhone').placeholder = '7XXXXXXX ou 8XXXXXXX';
                    document.getElementById('topupLimits').textContent = 'Min: 500 · Max: 150 000 FCFA';
                    document.getElementById('topupAmount').max = 150000;
                }
            };
        },

        async card(el) {
            const data = await API.get('/accounts');
            const comptes = data.comptes || [];
            const firstCompte = comptes[0];
            let carte = null;
            if (firstCompte) {
                const cardData = await API.get(`/accounts/${firstCompte.id}/card?full=true`);
                carte = cardData.carte;
            }
            el.innerHTML = carte ? `
            <div style="max-width:600px;margin:0 auto">
                <div style="display:flex;justify-content:center;margin-bottom:var(--space-8)" class="stagger-item">
                    <div class="bank-card-container" id="bankCard" onclick="this.classList.toggle('flipped')">
                        <div class="bank-card-inner">
                            <div class="bank-card-front">
                                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--space-4)">
                                    <div style="font-family:var(--font-display);font-size:var(--text-lg);font-weight:700">TogoBank</div>
                                    <span class="badge badge-${carte.statut==='active'?'success':'danger'}">${carte.statut}</span>
                                </div>
                                <div class="hero-card-chip"></div>
                                <div style="font-family:var(--font-mono);font-size:var(--text-xl);letter-spacing:0.15em;margin:var(--space-4) 0">${carte.numero_complet || carte.numero_masque}</div>
                                <div style="display:flex;justify-content:space-between;align-items:flex-end">
                                    <div>
                                        <div style="font-size:0.65rem;opacity:0.7">TITULAIRE</div>
                                        <div style="font-weight:600;letter-spacing:0.05em">${carte.nom_porteur}</div>
                                    </div>
                                    <div>
                                        <div style="font-size:0.65rem;opacity:0.7">EXPIRE</div>
                                        <div class="font-mono">${carte.date_expiration}</div>
                                    </div>
                                </div>
                            </div>
                            <div class="bank-card-back">
                                <div class="card-stripe"></div>
                                <div style="margin-top:var(--space-4)">
                                    <div style="font-size:var(--text-xs);opacity:0.7;margin-bottom:4px">CVV</div>
                                    <div class="card-cvv-area font-mono">${carte.cvv || '***'}</div>
                                </div>
                                <div style="margin-top:var(--space-4);font-size:var(--text-xs);opacity:0.6;line-height:1.5">
                                    Cette carte est la propriété de TogoBank Digital. Pour toute utilisation frauduleuse, veuillez appeler le +228 90 00 00 01.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <p style="text-align:center;font-size:var(--text-sm);color:var(--text-tertiary);margin-bottom:var(--space-6)">
                    <i class="fas fa-hand-pointer"></i> Cliquez sur la carte pour voir le CVV
                </p>
                <div class="card stagger-item">
                    <div style="display:flex;gap:var(--space-3);flex-wrap:wrap">
                        <button class="btn btn-${carte.statut==='active'?'danger':'success'}" onclick="App.toggleCard('${firstCompte.id}')">
                            <i class="fas fa-${carte.statut==='active'?'lock':'unlock'}"></i>
                            ${carte.statut==='active'?'Bloquer':'Débloquer'} la carte
                        </button>
                        <div style="flex:1"></div>
                        <div style="text-align:right">
                            <div style="font-size:var(--text-sm);color:var(--text-tertiary)">Plafond</div>
                            <div class="font-mono" style="font-weight:700">${App.formatMoney(carte.plafond)}</div>
                        </div>
                    </div>
                </div>
            </div>` : '<div class="empty-state"><div class="empty-state-icon"><i class="fas fa-credit-card"></i></div><p>Aucune carte disponible</p></div>';
        },

        async notifications(el) {
            // Simple notifications list from API user context
            el.innerHTML = `<div class="card stagger-item"><div class="card-header"><h3 class="card-title">Notifications</h3></div><div id="notifList"><div class="loader"><div class="loader-spinner"></div></div></div></div>`;
            // We'll use a simple mock since notifications don't have their own list endpoint yet
            el.querySelector('#notifList').innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon"><i class="fas fa-bell"></i></div>
                    <div class="empty-state-title">Tout est lu</div>
                    <p>Vous n'avez pas de nouvelles notifications.</p>
                </div>
            `;
        },

        async profile(el) {
            const res = await API.get('/auth/me');
            if (res.error) { el.innerHTML = `<p>${res.error}</p>`; return; }
            const u = res.user;
            el.innerHTML = `
            <div style="max-width:600px;margin:0 auto">
                <div class="card stagger-item" style="text-align:center;padding:var(--space-8)">
                    <div class="avatar avatar-xl" style="margin:0 auto var(--space-4)">${u.prenom?.[0]}${u.nom?.[0]}</div>
                    <h2>${u.prenom} ${u.nom}</h2>
                    <p style="color:var(--text-tertiary)">${u.email}</p>
                    <div style="display:flex;gap:var(--space-3);justify-content:center;margin-top:var(--space-4)">
                        <span class="badge badge-blue">${u.type_client}</span>
                        <span class="badge badge-${u.kyc_valide?'success':'warning'}">${u.kyc_valide?'KYC Vérifié':'KYC En attente'}</span>
                    </div>
                </div>
                <div class="card stagger-item" style="margin-top:var(--space-6)">
                    <h3 class="card-title" style="margin-bottom:var(--space-4)">Informations personnelles</h3>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4)">
                        <div><div class="form-label">N° Client</div><div class="font-mono">${u.numero_client}</div></div>
                        <div><div class="form-label">Téléphone</div><div>${u.telephone}</div></div>
                        <div><div class="form-label">Ville</div><div>${u.ville || '—'}</div></div>
                        <div><div class="form-label">Langue</div><div>${u.langue === 'fr' ? 'Français' : u.langue}</div></div>
                        <div><div class="form-label">Membre depuis</div><div>${App.formatDate(u.created_at)}</div></div>
                        <div><div class="form-label">Dernière connexion</div><div>${App.formatDate(u.derniere_connexion)}</div></div>
                    </div>
                </div>
            </div>`;
        },

        async admin(el) {
            const data = await API.get('/admin/dashboard');
            if (data.error) { el.innerHTML = `<div class="empty-state"><p>${data.error}</p></div>`; return; }
            const k = data.kpis;
            el.innerHTML = `
            <div class="grid grid-4 stagger-item">
                <div class="card stat-card"><div class="stat-icon blue"><i class="fas fa-users"></i></div><div><div class="stat-value">${k.total_utilisateurs}</div><div class="stat-label">Utilisateurs</div></div></div>
                <div class="card stat-card"><div class="stat-icon green"><i class="fas fa-check-circle"></i></div><div><div class="stat-value">${k.utilisateurs_actifs}</div><div class="stat-label">Actifs</div></div></div>
                <div class="card stat-card"><div class="stat-icon gold"><i class="fas fa-exchange-alt"></i></div><div><div class="stat-value">${k.total_transactions}</div><div class="stat-label">Transactions</div></div></div>
                <div class="card stat-card"><div class="stat-icon red"><i class="fas fa-id-card"></i></div><div><div class="stat-value">${k.kyc_en_attente}</div><div class="stat-label">KYC en attente</div></div></div>
            </div>
            <div class="grid grid-2" style="margin-top:var(--space-6)">
                <div class="card stagger-item">
                    <h3 class="card-title" style="margin-bottom:var(--space-4)">Volume total des transactions</h3>
                    <div class="font-display" style="font-size:var(--text-3xl);font-weight:700">${App.formatMoney(k.volume_total)}</div>
                    <div style="color:var(--text-tertiary);font-size:var(--text-sm)">Total des dépôts : ${App.formatMoney(k.total_depots)}</div>
                </div>
                <div class="card stagger-item">
                    <h3 class="card-title" style="margin-bottom:var(--space-4)">Nouveaux clients</h3>
                    ${(data.nouveaux_clients || []).slice(0,5).map(u => `
                    <div style="display:flex;align-items:center;gap:var(--space-3);padding:var(--space-2) 0;border-bottom:1px solid var(--border-light)">
                        <div class="avatar" style="width:32px;height:32px;font-size:0.7rem">${u.prenom?.[0]}${u.nom?.[0]}</div>
                        <div style="flex:1"><div style="font-weight:600;font-size:var(--text-sm)">${u.prenom} ${u.nom}</div><div style="font-size:var(--text-xs);color:var(--text-tertiary)">${u.email}</div></div>
                        <span class="badge badge-${u.statut==='actif'?'success':'warning'}">${u.statut}</span>
                    </div>
                    `).join('')}
                </div>
            </div>`;
        },

        async savings(el) {
            const data = await API.get('/accounts');
            const epargnes = (data.comptes || []).filter(c => c.type_compte === 'epargne');
            el.innerHTML = `
            <div style="max-width:600px;margin:0 auto">
                ${epargnes.length > 0 ? epargnes.map(c => `
                <div class="card stagger-item" style="margin-bottom:var(--space-4)">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:var(--space-4)">
                        <div><h3>${c.libelle}</h3><div class="font-mono" style="font-size:var(--text-xs);color:var(--text-tertiary)">${c.numero_compte}</div></div>
                        <span class="badge badge-success">${c.statut}</span>
                    </div>
                    <div class="font-display" style="font-size:var(--text-3xl);font-weight:700;margin-bottom:var(--space-4)">${App.formatMoney(c.solde)}</div>
                    <div class="progress-bar"><div class="progress-fill" style="width:${Math.min(100, (c.solde / 2000000) * 100)}%"></div></div>
                    <div style="display:flex;justify-content:space-between;margin-top:var(--space-2);font-size:var(--text-xs);color:var(--text-tertiary)">
                        <span>0 FCFA</span><span>Objectif : 2 000 000 FCFA</span>
                    </div>
                </div>`).join('') :
                `<div class="card stagger-item">
                    <div class="empty-state"><div class="empty-state-icon"><i class="fas fa-piggy-bank"></i></div><div class="empty-state-title">Pas encore d'épargne</div><p>Créez un compte épargne pour commencer.</p>
                    <button class="btn btn-primary" style="margin-top:var(--space-4)" onclick="App.openNewAccount()"><i class="fas fa-plus"></i> Créer un compte épargne</button></div>
                </div>`}
            </div>`;
        },

        async beneficiaries(el) {
            el.innerHTML = `
            <div class="card stagger-item">
                <div class="card-header">
                    <h3 class="card-title">Mes bénéficiaires</h3>
                    <button class="btn btn-primary btn-sm"><i class="fas fa-plus"></i> Ajouter</button>
                </div>
                <div class="empty-state">
                    <div class="empty-state-icon"><i class="fas fa-users"></i></div>
                    <div class="empty-state-title">Module bénéficiaires</div>
                    <p>Gérez vos contacts pour des virements rapides.</p>
                </div>
            </div>`;
        },

        async security(el) {
            el.innerHTML = `
            <div style="max-width:600px;margin:0 auto">
                <div class="card stagger-item" style="margin-bottom:var(--space-6)">
                    <h3 class="card-title" style="margin-bottom:var(--space-4)"><i class="fas fa-lock"></i> Changer le mot de passe</h3>
                    <form id="changePwdForm">
                        <div class="form-group"><label class="form-label">Mot de passe actuel</label><input type="password" class="form-input" id="curPwd" required></div>
                        <div class="form-group"><label class="form-label">Nouveau mot de passe</label><input type="password" class="form-input" id="newPwd" required></div>
                        <div class="form-group"><label class="form-label">Confirmer</label><input type="password" class="form-input" id="confPwd" required></div>
                        <button type="submit" class="btn btn-primary btn-block">Modifier le mot de passe</button>
                    </form>
                </div>
                <div class="card stagger-item">
                    <h3 class="card-title" style="margin-bottom:var(--space-4)"><i class="fas fa-shield-halved"></i> Authentification à deux facteurs</h3>
                    <p style="color:var(--text-secondary);font-size:var(--text-sm);margin-bottom:var(--space-4)">Ajoutez une couche de sécurité supplémentaire avec Google Authenticator.</p>
                    <button class="btn btn-secondary"><i class="fas fa-qrcode"></i> Activer la 2FA</button>
                </div>
            </div>`;
            document.getElementById('changePwdForm')?.addEventListener('submit', async (e) => {
                e.preventDefault();
                if (document.getElementById('newPwd').value !== document.getElementById('confPwd').value) {
                    App.toast('Les mots de passe ne correspondent pas', 'error'); return;
                }
                const res = await API.post('/auth/change-password', {
                    current_password: document.getElementById('curPwd').value,
                    new_password: document.getElementById('newPwd').value,
                });
                if (res.error) App.toast(res.error, 'error');
                else App.toast(res.message, 'success');
            });
        },
    },

    /* ========== CHARTS ========== */
    initDashboardCharts(txs, credits, debits) {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
        const txtColor = isDark ? '#94A3B8' : '#64748B';

        // Balance chart
        const balCtx = document.getElementById('balanceChart')?.getContext('2d');
        if (balCtx) {
            if (this.charts.balance) this.charts.balance.destroy();
            const labels = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc'];
            const vals = labels.map((_, i) => Math.floor(500000 + Math.random() * 1500000));
            this.charts.balance = new Chart(balCtx, {
                type: 'line',
                data: {
                    labels,
                    datasets: [{
                        label: 'Solde (FCFA)',
                        data: vals,
                        borderColor: '#2563EB',
                        backgroundColor: 'rgba(37,99,235,0.08)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        borderWidth: 2.5,
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { display: false }, ticks: { color: txtColor, font: { size: 11 } } },
                        y: { grid: { color: gridColor }, ticks: { color: txtColor, font: { size: 11 }, callback: v => (v/1000)+'K' } }
                    }
                }
            });
        }

        // Flow chart
        const flowCtx = document.getElementById('flowChart')?.getContext('2d');
        if (flowCtx) {
            if (this.charts.flow) this.charts.flow.destroy();
            this.charts.flow = new Chart(flowCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Crédits', 'Débits'],
                    datasets: [{
                        data: [credits || 1, debits || 1],
                        backgroundColor: ['#10B981', '#EF4444'],
                        borderWidth: 0,
                        borderRadius: 4,
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: {
                        legend: { position: 'bottom', labels: { color: txtColor, padding: 16, font: { size: 12 } } }
                    }
                }
            });
        }
    },

    /* ========== HELPERS ========== */
    formatMoney(n) {
        if (n == null) return '0 FCFA';
        return new Intl.NumberFormat('fr-FR').format(Math.round(n)) + ' FCFA';
    },
    formatDate(d) {
        if (!d) return '—';
        return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
    },

    toast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-icon"><i class="fas ${icons[type] || icons.info}"></i></div>
            <div class="toast-content"><div class="toast-title">${type === 'success' ? 'Succès' : type === 'error' ? 'Erreur' : 'Info'}</div><div class="toast-message">${message}</div></div>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;
        container.appendChild(toast);
        setTimeout(() => { toast.classList.add('toast-closing'); setTimeout(() => toast.remove(), 300); }, 4000);
    },

    /* ========== MOBILE MENU ========== */
    initMobileMenu() {
        document.getElementById('mobileMenuBtn')?.addEventListener('click', () => {
            document.getElementById('sidebar').classList.toggle('open');
            document.getElementById('sidebarOverlay').classList.toggle('active');
        });
        document.getElementById('sidebarOverlay')?.addEventListener('click', () => {
            document.getElementById('sidebar').classList.remove('open');
            document.getElementById('sidebarOverlay').classList.remove('active');
        });
        document.querySelectorAll('.nav-item, .bottom-nav-item').forEach(el => {
            el.addEventListener('click', () => {
                document.getElementById('sidebar').classList.remove('open');
                document.getElementById('sidebarOverlay').classList.remove('active');
            });
        });
    },

    /* ========== MODALS ========== */
    initModal() {
        document.getElementById('modalOverlay')?.addEventListener('click', (e) => {
            if (e.target === document.getElementById('modalOverlay')) this.closeModal();
        });
    },
    openModal(content) {
        document.getElementById('modalContent').innerHTML = content;
        document.getElementById('modalOverlay').classList.add('active');
    },
    closeModal() {
        document.getElementById('modalOverlay').classList.remove('active');
    },

    async openNewAccount() {
        this.openModal(`
            <div class="modal-header"><h3 class="modal-title">Nouveau compte</h3><button class="modal-close" onclick="App.closeModal()">×</button></div>
            <form id="newAcctForm">
                <div class="form-group"><label class="form-label">Type de compte</label>
                    <select class="form-input form-select" id="newAcctType">
                        <option value="courant">Courant</option><option value="epargne">Épargne</option><option value="pro">Professionnel</option><option value="jeune">Jeune</option>
                    </select>
                </div>
                <div class="form-group"><label class="form-label">Nom du compte</label><input type="text" class="form-input" id="newAcctLabel" placeholder="Ex: Compte Vacances"></div>
                <button type="submit" class="btn btn-primary btn-block">Créer le compte</button>
            </form>
        `);
        document.getElementById('newAcctForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const res = await API.post('/accounts', { type_compte: document.getElementById('newAcctType').value, libelle: document.getElementById('newAcctLabel').value });
            if (res.error) { App.toast(res.error, 'error'); return; }
            App.toast('Compte créé ! 🎉', 'success');
            App.closeModal();
            App.renderPage('accounts');
        });
    },

    async toggleCard(compteId) {
        const res = await API.post(`/accounts/${compteId}/card/toggle`);
        if (res.error) { this.toast(res.error, 'error'); return; }
        this.toast(res.message, 'success');
        this.renderPage('card');
    },
};

// Start
document.addEventListener('DOMContentLoaded', () => App.init());
