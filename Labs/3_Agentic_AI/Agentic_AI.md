# Agentic AI Lab: Network Supervisor Assistant - NSA 

![alt text](attachments/ATT_IBM_logo.png)

This use case is about an AI-powered assistant supporting a Network Supervisor in managing service disruptions. The Supervisor is responsible for monitoring the health of regional networks, diagnosing incidents, coordinating across infrastructure and communications, and ensuring timely remediation to minimize downtime. We apply an agentic solution based on watsonx Orchestrate and watsonx.ai to optimize these processes.  

---

## The Problem  
A large telecommunications provider faces frequent challenges in its Network Operations Center (NOC). Supervisors often deal with fragmented monitoring tools, siloed logs, and manual processes when diagnosing and resolving service disruptions. This results in long mean-time-to-resolution (MTTR), delayed communications to field teams, and occasional gaps in incident handovers. The manual coordination between teams further slows down operations, leading to increased costs and customer dissatisfaction.  

---

## Architecture  

![alt text](attachments/MultiAgentArchitecture.png)

- ##### Network Status Agent:

  - **Purpose**: Answers queries about the operational status of the network — including regions, sites, nodes, and active incidents.
  - **Tooling**: This agent connects to a **get_data tool** provided through an OpenAPI JSON file, enabling retrieval of up-to-date network data.
  - **Usage**: Handles queries like "What is the status of site S002?" or "Are there any ongoing outages in the Northeast region?"

  ##### Communications Agent

  - **Purpose**: Drafts professional and concise email updates for internal or external stakeholders about incidents or operational changes.
  - **Tooling**: This agent integrates with **Outlook** using an imported **OpenAPI JSON tool**, which enables it to send notification emails automatically.
  - **Usage**: When the Supervisor requests an incident update for the "Los Angeles AT&T Network team," this agent generates the email body and sends it through Outlook.

  ##### Incident Diagnosis Agent

  - **Purpose**: Analyzes incident logs, identifies the most likely **root cause**, and recommends a **resolution plan**.
  - **Tools**: Connects to a log analysis tool.
  - **Knowledge Sources**: Uses an incident resolution knowledge base for remediation steps.
  - **Output**: Always provides both the error type and the recommended resolution plan.

  ##### Server Status Agent

  - **Purpose**: Verifies whether a specific server or URL is currently online and reachable.
  - **Tools**: Uses a server check tool to confirm availability.
  - **Usage**: Handles requests like "Check if ATT.com is up."

  ##### Supervisor Agent

  - **Purpose**: Acts as the **routing agent**, interpreting user queries and delegating tasks to the right specialized agent.
  - **Collaborators**:
    - **Network Status Agent** → for network/site health checks.
    - **Server Status Agent** → for server reachability.
    - **Incident Diagnosis Agent** → for log analysis and remediation.
    - **Communications Agent** → for drafting and sending updates.
  - **User Experience**: Provides a natural language interface for the Supervisor, serving as the single entry point for all incident-related queries.

  Together, these agents form the backbone of the **Supervisor Assistant**. The Supervisor Agent orchestrates their interactions so that complex workflows (incident detection → diagnosis → remediation → communication) can be completed in a seamless conversational flow. Lets get started!

---

## Step-by-step Instructions  

Option 1: watsonx Orchestrate UI Only

Option 2: using ADK 

## Table of Contents

- [Introduction](#introduction)
- [Lab 1: Create Your First Agent](#lab-1-create-your-first-agent)
  - [The Network Status Agent](#the-network-status-agent)
  - [The Communication Agent](#the-communication-agent)
- [Part 2: Agent Development Kit](#part-2-agent-development-kit)
  - [The Incident Diagnosis Agent](#the-incident-diagnosis-agent)
  - [The Server Status Agent](#the-server-status-agent)
  - [The Supervisor Agent](#the-supervisor-agent)
- [Summary](#summary)

<details open id="introduction">
<summary><h2>Introduction</h2></summary>
In this lab, we will configure a set of 4 agents and 1 supervisor agent inside **Watsonx Orchestrate**. Each agent has a distinct responisbility and a unique toolset to comeplete a specific role in the incident response agentic system. The **Supervisor Agent** coordinates work among the agents by orchestrating requests to the appropriate agent. Below you will find an outline of all the agents we will build during this lab.


---

<details open id="pre-requisites">
<summary><h3>Pre-requisites</h3></summary>
</details>
<details open id="watsonx-orchestrate-setup">
<summary><h3>Launch Watsonx Orchestrate</h3></summary>

Watsonx Orchestrate is IBM's platform for creating, managing, and running AI-driven digital workers and agentic flows. In this bootcamp, you will be provided an IBM Cloud SaaS instance of Orchestrate. Follow the steps below to start your Orchestrate Instance:

1. **Access your Orchestrate Instance**

   - In the **IBM Cloud Dashboard navigate to the Resource List using the hamburger menu on top left.** 
     
   - Under AI/ML click on **watsonx Orchestrate** and launch the application.
     ![alt text](attachments/cloud_resource_list.png)
     ![alt text](attachments/Orchestrate_launch_page.png)

   - If you don't see any resources under AI/ML in your IBM Cloud Account kindly reachout to an instructor for assistance.
   - Once you have access to an Orchestrate instance you may continue to the next section

</details>

<details open id="lab-1-create-your-first-agent">
<summary><h2>Step-1: Create Your First Agent</h2></summary>

Navigate to the Watsonx Orchestrate home page. In the left-hand navigation menu, click on build to expand the menu and click on "**Agent Builder**". Agents depend on tools to perform their functions. When you define an agent, you specify which tools it can use in the tools section. The system needs the tools to exist before it can validate and import an agent that references them. 

![alt text](attachments/wxo_homepage.png)

<details open id="the-network-status-agent">
<summary><h3>The Network Status Agent</h3></summary>
The Network Status Agent answers questions about network health (regions, sites, nodes, active incidents).
In this lab, it does not use a knowledge base. Instead, it calls a `get_data` tool defined via an OpenAPI JSON so responses are fetched live from the source.

**Step 1.** Import the OpenAPI tool (`get_data`)

- We will first import an external REST API as a tool. To do this we will import an OpenAPI Spec into WXO
  1. Navigate to the Agent Builder tab.
  
     
  
     ![alt text](attachments/wxo_homepage.png)
  
     
  
  2. Create tool → Add from file or MCP server"→ Upload the OpenAPI (assets/tools/get_data_openapi.json) → Select the "Get Data" operation → Done\*\*
  
     ![alt text](attachments/wxo_tool1.png)
     ![alt text](attachments/wxo_tool2_1.png)
     ![alt text](attachments/wxo_tool2_2.png)
     ![alt text](attachments/wxo_tool3.png)
     ![alt text](attachments/wxo_tool4.png)
  
  3. Verify you see an entry for `get_data` tool under the tools homepage.
  
  4. If you're using a shared environment change the name of your tool not to overwrite other users work.
     ![alt text](attachments/image-7.png)

**Step 2.** Create Network Status Agent

- Now we will create our first agent. We will add the tool above into it's toolset and test the results.

  1.  Navigate to the Agent Builder tab.
  2.  To create a new agent click on **All agents → Create Agent → Enter name and description for your agent → Create**

      ![alt text](attachments/wxo_agent1.png)
      ![alt text](attachments/wxo_agent2.png)

  3. Give your agent a name. `network_status_agent_(with initials)`
  4.  Add the following description for your agent.
      ```
      The Network Status Agent specializes in answering inquiries about the current operational status of AT&T's network. It has access to up-to-date data about nodes sites, and services—such as cell towers, routers, and backhaul links—summarizes ongoing incidents, and provides a concise overview to the user.
      ```
  5.  Click Create
  
- Take some time to fully Explore the Agent screen
  ![alt text](attachments/wxo_agent3.png)

- Now that we've explored what the platform provides for our Agent lets add our tool.
  1.  Scroll down to the **Toolset** section and click on "Add Tool".
  2.  Since we have already added the `get_data` tool to our local instance, we can select and add it to the agent.
      ![alt text](attachments/wxo_agent4.png)
      ![alt text](attachments/wxo_agent5.png)
      ![alt text](attachments/wxo_agent6.png)
- Lastly we must add instructions for our agent. **This will explain to the LLM what to do**, and how to utilize its tools to acomplish the goal. It is crucial to provide instructions to let agents perform effectively. It decides the behavior of the agent and provides context for how to use its tools and agents.

  1.  Scroll down to the **Behavior** section and **add the following instructions.** 

      ```
      Answer questions about the operational status of AT&T's network based on the provided site and node data.This includes information about nodes, incidents, and overall health of regions or specific locations.
      
      Provide your answer as a concise summary. If a location, site ID, or region is mentioned, filter your response accordingly.
      ```

![alt text](attachments/wxo_agent7.png)



**Step 3.** **Now its time to test our agent**

- In the chat ask `What is the status of site S003?`The agent should call `get_data` behind the scenes.
- **Click on the resoning tab** and explore what it did to retrive the answer.
- `Can you provide me a table of all the cell towers in the system with their relevant status?`
- `Why is site S004 down?`

**Congratulations you've just completed building your frist Agent!** The **Network Status Agent** is ready. It will now route natural-language queries to the `get_data` tool to return live network status.

</details>

<details open id="the-communication-agent">
<summary><h3>The Communication Agent</h3></summary>

The **Communications Agent** is responsible for drafting clear and professional notification emails about network incidents or operational updates.

#### 1) Import the Outlook Email Tool

This tool provides the functionality for the agent to send emails via the Outlook Mail Server API.

- We will first import the Send Outlook Email tool. To do this we will import an OpenAPI Spec into WXO
  1.  Navigate to the Agent Builder tab.
      ![alt text](attachments/wxo_homepage.png)
  2.  Create tool → Add from file or MCP server"→ Upload the OpenAPI (wxo_assets/tools/outlook_email_openapi.json) → Select the "Send Email Outlook" operation → Done\*\*
      ![alt text](attachments/wxo_tool1.png)
      ![alt text](attachments/wxo_tool2_1.png)
      ![alt text](attachments/wxo_tool2_2.png)
      ![alt text](attachments/wxo_tool3.png)
      ![alt text](attachments/outlook_email_selection.png)
  3.  If you're using a shared environment change the name of your tool not to overwrite other users work.
      ![alt text](attachments/image-5.png)
      ![alt text](attachments/image-6.png)

#### 2) Create the Communications Agent

- Now we will create the Communications Agent.

  1. Navigate to the Agent Builder tab.

  2. To create a new agent click on **All agents → Create Agent → Enter name and description for your agent → Create**

  3. Give your agent a name. `communications_agent_(with initials)`

  4. Add the following description for your agent.

     ```
      The Communications Agent specializes in drafting internal or external notification emails and messages regarding network incidents or operational updates.
     ```

  5. Click Create

     ![alt text](attachments/wxo_agent1.png)
     ![alt text](attachments/communication_agent_creation_page.png)

  6. 

- Lastly add instructions to the Communicaitons Agent

  1.  Scroll down to the **Behavior** section and add the following instructions.

  ```
  - Your response **must strictly follow this format** when asked to draft an email:
  - Write a concise and professional message about a network incident or operational update.
  - Start with the subject line on the first line, then the message body on the next line.
  - Use actual line breaks (press Enter) — do not output \n as text.
  - Do not include preambles, labels, or extra formatting.
  - Tailor the message to the relevant team or stakeholder group if specified (e.g., Network Ops,     Engineering, External Vendor).
  - Do not ask for the recipient email address during drafting.
  - Only use the 'Send Email Outlook' tool when the user explicitly asks to send an email.
  - When using the Send email tool ensure to convert the drafted email into HTML for the content field.
  - If the user asks to send an email but does not provide a recipient email address, do not send the email under any circumstances until the user inputs "email" field
  - Immediately ask the user: "What is the recipient's email address?"
  - Wait for the user to provide the email. Do not proceed until the user explicitly enters it.
  - *Strictly follow this**: After the user provides recipient email address: Display it back to the user and ask: "Please confirm if this is correct: [email]".
  - Do not ask unrelated follow-up questions.
  - Respond only with the information requested.

  Tool Access:
  Use the `Send Email Outlook` to send the email to the email provided

- Ask the agent: `Draft an email invite about an Agentic AI bootcamp in New York around October.`
- The agent should generate a professional email body.
- If the Outlook tool is configured, you can also instruct it to send the email directly by asking `Send the above email to {email_id}`.





**[Add steps to create 2 agents and add tools already there]**







  6. Save. This may take 1 min or two.
- Configure the Knowledge Base
  1. Scroll down to the Knowledge section and click `Edit knowledge settings`
     ![alt text](attachments/kb4.png)
  2. Modify the retrieval criteria and save
     ![alt text](attachments/kb5.png)



#### 4) Quick sanity checks

- Test your agent with the following prompt: `Here is the log: "UPS unit failed at site S002. Generator did not auto-start. Site running on battery only."`
- The agent should respond with both the **error type** and the **resolution plan**.

#### 5) Common troubleshooting tips

The **Incident Diagnosis Agent** is now ready. It can be invoked directly or through the Supervisor Agent to analyze logs and recommend remediation steps.

</details>

<details open id="the-server-status-agent">
<summary><h3>The Server Status Agent</h3></summary>
The **Server Status Agent** checks whether a given server or URL is reachable.  
This is useful for quickly validating if a service endpoint is online when an incident is reported.

#### 1) Import the Server Status Tool

This tool allows the agent to test HTTP/HTTPS endpoints and return whether they are up or down.

- Run: `orchestrate tools import -k python -f assets/tools/check_server_status_tool.py`
- Verify: `orchestrate tools list` → you should see `check_server_status`

> **Console option (SaaS):** From the Orchestrate web console, navigate to **Tools → Add tool → Python**, then upload `assets/tools/check_server_status_tool.py`.

#### 2) Import the Server Status Agent YAML

This binds the **Server Status Agent** to the `check_server_status` tool you just imported.

- Run: `orchestrate agents import -f assets/agents/server_status_agent.yaml`
- Verify: `orchestrate agents list` → you should see `server_status_agent`

> **Console option (SaaS):** Go to **Agents → Add agent**, upload `assets/agents/server_status_agent.yaml`, then save.

#### 3) Quick sanity checks

- Ask: "Check if ATT.com is up."
- The agent should call the `check_server_status` tool and return whether the server is reachable.
- If no response or an error occurs, confirm the tool is present and correctly linked to the agent.

#### 4) Common troubleshooting tips

- **Tool not found:** Re-run `orchestrate tools list`. If `check_server_status` is missing, re-import it.
- **Incorrect binding:** Verify that the agent YAML references `check_server_status` exactly as the tool name.
- **Network restrictions:** Ensure the SaaS environment can reach the target server (some internal endpoints may be blocked).

The **Server Status Agent** is now ready. It can be queried directly or invoked by the Supervisor Agent to check server availability in real time.

</details>

<details open id="the-supervisor-agent">
<summary><h3>The Supervisor Agent</h3></summary>

The **Supervisor Agent** acts as the routing brain for this use case. It interprets a user's request and delegates the task to the correct specialist agent:

- **Network Status Agent** → network/site health questions
- **Server Status Agent** → server/URL reachability
- **Incident Diagnosis Agent** → log analysis and remediation recommendations
- **Communications Agent** → drafting/sending stakeholder updates

This section wires up the Supervisor so it can orchestrate the end-to-end flow from detection → diagnosis → remediation → communication.

#### 1) Create the Supervisor Agent

This [add instructions to create supervisor agent]



#### 2) 2. Add Collaborator Agents to the NOC_Supervisor_Agent

- Go to Manage Agents - > Click on NOC_Supervisor_Agent
- Click on Toolset -> Add Agent as shown in screenshot
  ![alt text](attachments/image.png)
- Choose "Add from Local Instance" option
  ![alt text](attachments/image-1.png)
- Click on 4 Agents you created as shown below:
  - network_status_agent
  - server_status_agent
  - incident_diagnosis_agent
  - communications_agent
- Click on Add to Agent
  ![alt text](attachments/image-2.png)

The **Supervisor Agent** is now ready. It provides a single conversational entry point and automatically delegates tasks to the right agent, enabling an end-to-end incident flow.

#### 3) Testing the Supervisor Agent (routing behavior)

Try these natural-language prompts to validate routing:

- "**What's the status of site S002?**" → should route to **Network Status Agent** (calls `get_data`)
- "**Check if ATT.com is up.**" → should route to **Server Status Agent** (calls `check_server_status`)
- "**Here's an incident log 'BGP session dropped due to incorrect neighbor settings in config push from NOC.' what's the root cause and fix?**" → should route to **Incident Diagnosis Agent** (uses `diagnose_incident_log`, consults resolution guides if configured)
- "**Draft a clear email addressing the above issue and the resolution steps involved.**" → should route to **Communications Agent**
- "**Send the above email to {email_id}**" → (send via Outlook if configured)

#### 5) Bonus Challenge: Override the Default Greeting

By default, new agents start with "Hello! I am watsonx Orchestrate, an AI assistant, created by IBM. How can I help you today?". You can override this in the Orchestrate Console.

1. Go to the Orchestrate Console.
2. In the left-hand navigation (hamburger menu), go to Build → Agent Builder.
3. Click on `supervisor_agent` to view its details.
4. Edit the Agent Behavior in a way it says "Hello, I'm the Supervisor. I can help you check network and server status, diagnose incidents, or draft communications. How can I help you today?"
   > Here are some things you may want to try:
   >
   > - Role clarity: Specify to the agent that it should clearly identify itself as the Supervisor.
   > - Task framing: Tell the agent to summarize the types of requests it can handle (network checks, incident diagnosis, communications).
   > - Override default: Make sure to instruct the agent to fully replace the standard watsonx greeting with this custom introduction.
   > - Constraints: Specify that the agent should not mention IBM or watsonx.
   > - Tone & personality: You can guide the agent to adopt a professional, supportive, concise, or friendly tone to make the greeting more engaging.

✅ The next time you start a chat, the agent should greet with your customized introduction instead of the default watsonx Orchestrate greeting.

</details>

</details>

<details id="summary">
<summary><h2>Summary</h2></summary>

In this lab, we explored the use case of a Supervisor managing network incidents with the help of an agentic AI solution. We began by creating specialized agents for network status checks, server availability, incident diagnosis, and stakeholder communications. Each agent was connected to the right tools and data sources — for example, the Network Status Agent used an OpenAPI tool to fetch live site data, while the Communications Agent leveraged Outlook integration to send updates.

Finally, we brought everything together through the **Supervisor Agent**, which serves as the main conversational entry point. From this single interface, the Supervisor can ask natural language questions and the system will automatically route the request to the appropriate agent.

This exercise provides a reference implementation to help you understand how multiple specialized agents can be orchestrated in **watsonx Orchestrate (SaaS)**. Some aspects are simulated, and in a production environment you would extend the integrations with real systems of record, monitoring platforms, and communication services. A truly agentic solution would go further by adding reasoning and planning capabilities, allowing the system to autonomously investigate, resolve, and communicate about incidents end-to-end.

Our goal here is to give you a starting point and spark ideas about how to apply agentic AI in real operational contexts. With these foundations, you can begin experimenting with automating parts of your own workflows and consider where autonomous AI decision-making could add the most value.

</details>
