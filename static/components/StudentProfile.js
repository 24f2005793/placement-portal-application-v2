export default {
    template: `
        <div class="row justify-content-center mt-4">
            <div class="col-md-8">
                <div class="card shadow-sm">
                    <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
                        <h4 class="mb-0">Student Profile</h4>
                        <button class="btn btn-sm btn-outline-light" @click="$router.go(-1)">Back</button>
                    </div>
                    <div class="card-body" v-if="student">
                        <div class="row mb-3">
                            <div class="col-sm-4 fw-bold">Name:</div>
                            <div class="col-sm-8">{{ student.first_name }} {{ student.last_name }}</div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-sm-4 fw-bold">Email:</div>
                            <div class="col-sm-8">{{ student.email }}</div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-sm-4 fw-bold">Branch:</div>
                            <div class="col-sm-8">{{ student.branch || 'Not provided' }}</div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-sm-4 fw-bold">CGPA:</div>
                            <div class="col-sm-8">{{ student.cgpa || 'Not provided' }}</div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-sm-4 fw-bold">Account Status:</div>
                            <div class="col-sm-8">
                                <span class="badge" :class="student.active ? 'bg-success' : 'bg-danger'">
                                    {{ student.active ? 'Active' : 'Blacklisted' }}
                                </span>
                            </div>
                        </div>
                        
                        <hr>
                    </div>
                    <div class="card-body text-center" v-else>
                        <p>Loading student data...</p>
                    </div>
                </div>
            </div>
        </div>
    `,
    data() {
        return {
            student: null,
            token: localStorage.getItem('auth-token')
        }
    },
    async mounted() {
        // Fetch student details using the ID parameter from the URL
        const studentId = this.$route.params.id;
        try {
            const response = await fetch(`/api/students/${studentId}`, {
                headers: { 'Authentication-Token': this.token }
            });
            if (response.ok) {
                this.student = await response.json();
            }
        } catch (err) {
            console.error("Error fetching student profile", err);
        }
    }
}