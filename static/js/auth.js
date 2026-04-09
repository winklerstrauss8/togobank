/**
 * TogoBank Digital — Auth Module
 * Gère les formulaires de connexion et d'inscription.
 */
const Auth = {
    renderLogin() {
        return `
            <div class="auth-header">
                <h2 class="auth-title">Bon retour ! 👋</h2>
                <p class="auth-subtitle">Connectez-vous à votre espace TogoBank</p>
            </div>
            <form id="loginForm">
                <div class="form-group">
                    <label class="form-label">Email ou téléphone</label>
                    <input type="text" class="form-input" id="loginIdentifier"
                        placeholder="ama@example.com ou 91234567" required autocomplete="username">
                </div>
                <div class="form-group">
                    <label class="form-label">Mot de passe</label>
                    <div style="position:relative">
                        <input type="password" class="form-input" id="loginPassword"
                            placeholder="••••••••" required autocomplete="current-password">
                        <button type="button" class="btn-icon" id="toggleLoginPwd"
                            style="position:absolute;right:8px;top:50%;transform:translateY(-50%);background:none;border:none;color:var(--text-tertiary)">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--space-6)">
                    <label style="display:flex;align-items:center;gap:var(--space-2);font-size:var(--text-sm);color:var(--text-secondary);cursor:pointer">
                        <input type="checkbox" id="rememberMe"> Se souvenir de moi
                    </label>
                    <a href="#" style="font-size:var(--text-sm)">Mot de passe oublié ?</a>
                </div>
                <button type="submit" class="btn btn-primary btn-block btn-lg" id="loginBtn">
                    <i class="fas fa-sign-in-alt"></i> Se connecter
                </button>
            </form>
            <div class="auth-footer">
                Pas encore de compte ? <a href="#register">Créer un compte</a>
            </div>
        `;
    },

    renderRegister() {
        return `
            <div class="auth-header">
                <h2 class="auth-title">Créer un compte 🚀</h2>
                <p class="auth-subtitle">Rejoignez TogoBank Digital en quelques minutes</p>
            </div>
            <div class="wizard-steps" id="wizardSteps">
                <div class="wizard-step active" data-step="1"></div>
                <div class="wizard-step" data-step="2"></div>
                <div class="wizard-step" data-step="3"></div>
            </div>
            <form id="registerForm">
                <div id="step1">
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4)">
                        <div class="form-group">
                            <label class="form-label">Prénom</label>
                            <input type="text" class="form-input" id="regPrenom" placeholder="Ama" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Nom</label>
                            <input type="text" class="form-input" id="regNom" placeholder="Koffi" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Email</label>
                        <input type="email" class="form-input" id="regEmail" placeholder="ama@example.com" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Téléphone</label>
                        <input type="tel" class="form-input" id="regTel" placeholder="91234567" required>
                    </div>
                    <button type="button" class="btn btn-primary btn-block btn-lg" onclick="Auth.nextStep(2)">
                        Continuer <i class="fas fa-arrow-right"></i>
                    </button>
                </div>
                <div id="step2" style="display:none">
                    <div class="form-group">
                        <label class="form-label">Type de compte</label>
                        <select class="form-input form-select" id="regType">
                            <option value="particulier">Particulier</option>
                            <option value="entreprise">Entreprise</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Ville</label>
                        <input type="text" class="form-input" id="regVille" placeholder="Lomé">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Date de naissance</label>
                        <input type="date" class="form-input" id="regDob">
                    </div>
                    <div style="display:flex;gap:var(--space-3)">
                        <button type="button" class="btn btn-secondary btn-block" onclick="Auth.nextStep(1)">
                            <i class="fas fa-arrow-left"></i> Retour
                        </button>
                        <button type="button" class="btn btn-primary btn-block" onclick="Auth.nextStep(3)">
                            Continuer <i class="fas fa-arrow-right"></i>
                        </button>
                    </div>
                </div>
                <div id="step3" style="display:none">
                    <div class="form-group">
                        <label class="form-label">Mot de passe</label>
                        <input type="password" class="form-inPput" id="regPassword" placeholder="Min. 8 caractères" required>
                        <div class="password-strength" id="pwdStrength">
                            <div class="password-bar"></div><div class="password-bar"></div>
                            <div class="password-bar"></div><div class="password-bar"></div>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Confirmer le mot de passe</label>
                        <input type="password" class="form-input" id="regPasswordConfirm" placeholder="••••••••" required>
                    </div>
                    <div class="form-group">
                        <label style="display:flex;align-items:flex-start;gap:var(--space-2);font-size:var(--text-sm);color:var(--text-secondary);cursor:pointer">
                            <input type="checkbox" id="regCGU" required style="margin-top:3px">
                            J'accepte les <a href="#">Conditions Générales d'Utilisation</a>
                        </label>
                    </div>
                    <div style="display:flex;gap:var(--space-3)">
                        <button type="button" class="btn btn-secondary btn-block" onclick="Auth.nextStep(2)">
                            <i class="fas fa-arrow-left"></i> Retour
                        </button>
                        <button type="submit" class="btn btn-primary btn-block" id="registerBtn">
                            <i class="fas fa-user-plus"></i> Créer mon compte
                        </button>
                    </div>
                </div>
            </form>
            <div class="auth-footer">
                Déjà inscrit ? <a href="#login">Se connecter</a>
            </div>
        `;
    },

    currentStep: 1,

    nextStep(step) {
        // Validate current step
        if (step > this.currentStep) {
            if (this.currentStep === 1) {
                const prenom = document.getElementById('regPrenom').value;
                const nom = document.getElementById('regNom').value;
                const email = document.getElementById('regEmail').value;
                const tel = document.getElementById('regTel').value;
                if (!prenom || !nom || !email || !tel) {
                    App.toast('Veuillez remplir tous les champs', 'error');
                    return;
                }
            }
        }

        document.getElementById(`step${this.currentStep}`).style.display = 'none';
        document.getElementById(`step${step}`).style.display = 'block';
        document.getElementById(`step${step}`).classList.add('animate-fade-in');
        this.currentStep = step;

        document.querySelectorAll('.wizard-step').forEach((el, i) => {
            el.className = 'wizard-step';
            if (i + 1 < step) el.classList.add('completed');
            if (i + 1 === step) el.classList.add('active');
        });
    },

    init() {
        // Login form
        document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('loginBtn');
            btn.disabled = true;
            btn.innerHTML = '<div class="loader-spinner" style="width:20px;height:20px;border-width:2px"></div> Connexion...';

            const res = await API.post('/auth/login', {
                email: document.getElementById('loginIdentifier').value,
                password: document.getElementById('loginPassword').value
            });

            if (res.error) {
                App.toast(res.error, 'error');
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Se connecter';
                return;
            }

            API.setAuth(res);
            App.toast(`Bienvenue, ${res.user.prenom} ! 🎉`, 'success');
            window.location.hash = '#dashboard';
        });

        // Register form
        document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const pwd = document.getElementById('regPassword').value;
            const pwdConfirm = document.getElementById('regPasswordConfirm').value;

            if (pwd !== pwdConfirm) {
                App.toast('Les mots de passe ne correspondent pas', 'error');
                return;
            }
            if (pwd.length < 8) {
                App.toast('Le mot de passe doit contenir au moins 8 caractères', 'error');
                return;
            }
            if (!document.getElementById('regCGU').checked) {
                App.toast('Veuillez accepter les CGU', 'error');
                return;
            }

            const btn = document.getElementById('registerBtn');
            btn.disabled = true;
            btn.innerHTML = '<div class="loader-spinner" style="width:20px;height:20px;border-width:2px"></div>';

            const res = await API.post('/auth/register', {
                prenom: document.getElementById('regPrenom').value,
                nom: document.getElementById('regNom').value,
                email: document.getElementById('regEmail').value,
                telephone: document.getElementById('regTel').value,
                password: pwd,
                type_client: document.getElementById('regType').value,
                ville: document.getElementById('regVille').value,
            });

            if (res.error) {
                App.toast(res.error, 'error');
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-user-plus"></i> Créer mon compte';
                return;
            }

            API.setAuth(res);
            App.toast('Compte créé avec succès ! 🎉', 'success');
            window.location.hash = '#dashboard';
        });

        // Toggle password visibility
        document.getElementById('toggleLoginPwd')?.addEventListener('click', function() {
            const input = document.getElementById('loginPassword');
            const icon = this.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.className = 'fas fa-eye-slash';
            } else {
                input.type = 'password';
                icon.className = 'fas fa-eye';
            }
        });

        // Password strength
        document.getElementById('regPassword')?.addEventListener('input', function() {
            const bars = document.querySelectorAll('.password-bar');
            const val = this.value;
            let strength = 0;
            if (val.length >= 8) strength++;
            if (/[A-Z]/.test(val)) strength++;
            if (/[0-9]/.test(val)) strength++;
            if (/[^A-Za-z0-9]/.test(val)) strength++;
            bars.forEach((bar, i) => {
                bar.className = 'password-bar';
                if (i < strength) {
                    bar.classList.add(strength <= 1 ? 'weak' : strength <= 2 ? 'medium' : 'strong');
                }
            });
        });
    }
};
