<template>
  <b-container>
    <b-row class="mb-5">
      <b-col md="6">
        <b-form-group
          label="Tool to search for:"
          label-for="filter"
          description="Search for strings or regular expressions"
        >
          <b-input-group>
            <b-form-input
              id="filter"
              v-model="filter"
              placeholder="Type and press enter to search"
              @keyup.esc.native="filter = ''"
              @keyup.enter.native="onQuery()"
            />
            <b-input-group-append>
              <b-btn
                :disabled="!filter"
                @click="filter = ''"
              >Clear (esc)</b-btn>
            </b-input-group-append>
          </b-input-group>
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
      axios.get(`http://localhost:8082/workflows.json`).then(r => {
        const workflows = r.data[0];
        Object.entries(workflows).forEach(([key, value]) => {
          const tools = value["tools"].reduce((acc, cur) => {
            acc.push(cur["name"]);
            return acc;
          }, []);
          this.workflows.push({
            source: key,
            workflow: value["name"],
            tools: [...tools].join(", ")
          });
        });
      });
    }
  }
};
</script>