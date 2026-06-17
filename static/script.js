// Step-1 : Import components
import Home from './components/Home.js';
import Navbar from './components/Navbar.js';


//Step -2 : Define path for components
const routes = [
    { path: '/', component: Home }
];


//Step -3 : Create router object to connect with app
const router = new VueRouter({
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