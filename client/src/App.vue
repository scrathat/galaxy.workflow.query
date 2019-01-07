<template>
  <div id="app">
    <b-jumbotron header="Galaxy Workflow Query" lead="Search workflows for tools used">
      <p>For more information:</p>
      <p>
        <b-link href="https://github.com/galaxyproject/galaxy/pull/7020">Galaxy PR 7020: Expose published workflows through API</b-link>
      </p>
      <p>
        <b-link href="https://github.com/frederikcoppens/galaxy_workflows_poc_app">frederikcoppens/galaxy_workflows_poc_app</b-link>
      </p>
      <p>
        Needs <code>allowed_origin_hostnames: localhost</code> in <code>config/galaxy.yml</code>
      </p>
    </b-jumbotron>
    <WorkflowQuery />
  </div>
</template>

<script>
import WorkflowQuery from "./components/WorkflowQuery.vue";

export default {
  name: "app",
  components: {
    WorkflowQuery
  }
};
</script>

<style>
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
