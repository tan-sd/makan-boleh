<template>
    <nav class="navbar navbar-expand-lg bg-dark navbar-dark">
        <div class="container-fluid">
            <router-link to="/" class="navbar-brand">
                <img src="../assets/images/logos/small_logos/MakanBoleh_logo_long_light_small.png" alt="MakanBoleh Logo" width="165">
            </router-link>

            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target=".navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                <span><font-awesome-icon icon="fa-solid fa-burger" /></span>
            </button>

            <div class="collapse navbar-collapse navbarSupportedContent">
                <ul class="navbar-nav mb-2 mb-lg-0" v-if="this.$store.state.isAuthenticated">
                    <!-- <p class="text-white my-auto mt-2 mt-md-0 fw-semibold fst-italic">Welcome {{ this.$store.state.user_details.first_name }} {{ this.$store.state.user_details.last_name }}!</p> -->
                    <p class="text-white my-auto mt-2 mt-md-0 fw-semibold fst-italic">Welcome {{ this.$store.state.username }}!</p>
                </ul>
            </div>

            <div class="collapse navbar-collapse navbarSupportedContent">
                <ul class="navbar-nav mb-2 mb-lg-0 ms-auto">
                    <li class="nav-item" v-if="this.$store.state.isAuthenticated">
                        <span class="nav-link" style="cursor: pointer" @click="logOut">Log out</span>
                    </li>
                    <li class="nav-item" v-else>
                        <router-link to="/login" class="nav-link">Login</router-link>
                    </li>
                    <li class="nav-item" v-if="this.$store.state.isAuthenticated">
                        <router-link to="/user" class="nav-link">User Profile</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link to="/forum" class="nav-link">Forum</router-link>
                    </li>
                </ul>

                <div class="d-flex justify-content-center button-container mx-auto mx-lg-0">
                    <FoodForm class="btn btn-main"/>
                </div>
            </div>
        </div>
    </nav>
</template>

<script>
import FoodForm from '../components/FoodForm.vue';

    export default{
        components: {
            FoodForm
        },
        props: [],

        data() {
            return {
                sessionUserName: null,
            }
        },
        methods: {
            logOut() {
                this.$store.state.isAuthenticated = false;
                this.$router.push('/');
            }
        },
    }
</script>


<style scoped>
    .button-container{
        width: 200px
    }
</style>