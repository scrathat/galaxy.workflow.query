<template>
    <b-container>
        <b-row class="mb-5">
            <b-col md="6">
                <b-form-group label="API Key:" label-for="apiKey" description="You can generate an API Key under User/Preferences/Manage API key.">
                    <b-form-input id="apiKey" v-model="apiKey" placeholder="Enter an API Key" />
                </b-form-group>
                <b-form-group label="Tool to search for:" label-for="filter" description="Search for strings or regular expressions">
                    <b-input-group>
                        <b-form-input id="filter" v-model="filter" placeholder="Type and press enter to search" @keyup.esc.native="filter = ''" @keyup.enter.native="onQuery()" />
                        <b-input-group-append>
                            <b-btn :disabled="!filter" @click="filter = ''">Clear (esc)</b-btn>
                        </b-input-group-append>
                    </b-input-group>
                </b-form-group>
            </b-col>
            <b-col md="6">
                <b-form-group label="Query the following Galaxy instances:">
                    <b-form-checkbox-group id="galaxyInstances" name="galaxyInstances" v-model="selectedInstances" :options="galaxyInstances">
                    </b-form-checkbox-group>
                </b-form-group>
            </b-col>
        </b-row>
        <b-row>
            <h1>Results</h1>
        </b-row>
        <b-row>
            <b-table :items="items" />
        </b-row>
    </b-container>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      apiKey: "",
      selectedInstances: ["http://localhost:8080"],
      galaxyInstances: [
        {
          text: "localhost:8080",
          value: "http://localhost:8080",
          disabled: true
        },
        { text: "usegalaxy.eu", value: "http://usegalaxy.eu", disabled: true },
        { text: "usegalaxy.org", value: "http://usegalaxy.org", disabled: true }
      ],
      show: true,
      filter: "",
      workflows: []
    };
  },
  computed: {
    items() {
      return this.workflows.filter(w =>
        w["tools"].match(new RegExp(this.filter, "i"))
      );
    }
  },
  methods: {
    onQuery() {
      this.workflows = [];
      for (const i of this.selectedInstances) {
        axios.get(`${i}/api/workflows?key=${this.apiKey}`).then(r => {
          let workflows = r.data;
          for (const w of workflows) {
            let tools = new Set();
            axios.get(`${i}${w["url"]}?key=${this.apiKey}`).then(r => {
              let steps = r.data["steps"];
              for (const s in steps) {
                if (steps[s]["type"] === "tool") {
                  tools.add(steps[s]["tool_id"]);
                }
              }
              this.workflows.push({
                workflow: w["name"],
                tools: [...tools].join(", ")
              });
            });
          }
        });
      }
    }
  }
};
</script>