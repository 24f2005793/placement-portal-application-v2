// Step-1 : Import components
import Home from './components/Home.js';
import Navbar from './components/Navbar.js';
import Login from './components/Login.js';
import Register from './components/Register.js';
import AdminDashboard from './components/AdminDashboard.js';
import CompanyDashboard from './components/CompanyDashboard.js';
import CreateDrive from './components/CreateDrive.js';
import StudentDashboard from './components/StudentDashboard.js';
import DriveProfile from './components/DriveProfile.js';
import StudentProfile from './components/StudentProfile.js'; 
import CompanyDrives from './components/CompanyDrives.js';
import DriveApplications from './components/DriveApplications.js';
import StudentHistory from './components/StudentHistory.js';


//Step -2 : Define path for components
const routes = [
    { path: '/', component: Home },
    { path: '/login',component: Login},
    { path: '/register',component: Register},
    { path: '/admin/dashboard',component: AdminDashboard},
    { path: '/company/dashboard',component: CompanyDashboard},
    { path: '/create-drive', component: CreateDrive },
    { path: '/student/dashboard', component: StudentDashboard },
    { path: '/drive/:id', component: DriveProfile },
    { path: '/student/:id', component: StudentProfile },
    { path: '/company-drives/:id', component: CompanyDrives },
    { path: '/drive-applications/:id', component: DriveApplications },
    { path: '/student-history', component: StudentHistory }
];


//Step -3 : Create router object to connect with app
const router = new VueRouter({
    mode: 'history',
    routes 
});


//Step -4 : Connect Vue with app 
new Vue({
    el: '#app',
    router: router, //for router-view
    components: {
        Navbar 
    }
});