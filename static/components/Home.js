export default {
    template: `
        <div>
            <div class="hero-section text-center mb-5">
                <h1 class="fw-bold mb-3">Placement Portal</h1>
                <p class="lead mb-4">
                    A simple platform that brings students, companies, and the placement cell
                    together in one place — from drive announcements to final results.
                </p>
                <div v-if="!isLoggedIn">
                    <router-link to="/login" class="btn btn-light btn-lg me-2">Login</router-link>
                    <router-link to="/register" class="btn btn-outline-light btn-lg">Register</router-link>
                </div>
                <div v-else>
                    <router-link :to="dashboardLink" class="btn btn-light btn-lg">Go to Dashboard</router-link>
                </div>
            </div>

            <div class="row g-4 mb-5">
                <div class="col-md-4">
                    <div class="card shadow-sm h-100">
                        <div class="card-body">
                            <div class="feature-icon mb-2">🎓</div>
                            <h5 class="fw-bold">For Students</h5>
                            <p class="text-muted mb-0">
                                Browse ongoing placement drives, check your eligibility at a glance,
                                apply in a click, and track every application from one dashboard.
                            </p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card shadow-sm h-100">
                        <div class="card-body">
                            <div class="feature-icon mb-2">🏢</div>
                            <h5 class="fw-bold">For Companies</h5>
                            <p class="text-muted mb-0">
                                Post new drives, set eligibility criteria, and review applicants —
                                without the back-and-forth emails.
                            </p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card shadow-sm h-100">
                        <div class="card-body">
                            <div class="feature-icon mb-2">🛠️</div>
                            <h5 class="fw-bold">For the Placement Cell</h5>
                            <p class="text-muted mb-0">
                                Approve companies and drives, monitor activity, and keep everything
                                organized from a single admin dashboard.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
    data() {
        return {
            isLoggedIn: !!localStorage.getItem('auth-token'),
            role: localStorage.getItem('role')
        }
    },
    computed: {
        dashboardLink() {
            if (this.role === 'admin') return '/admin/dashboard';
            if (this.role === 'company') return '/company/dashboard';
            if (this.role === 'student') return '/student/dashboard';
            return '/';
        }
    }
}