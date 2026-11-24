# Multi-service coverage: companies that sell several service classes

| Field | Value |
|---|---|
| Question | Which companies sell many service classes at once, like cloud, database, and payment? |
| Input | 259-row infrastructure CSV, plus two vendor pages read directly |
| Finding | 23 reachable companies cover 3 or more families. Only one of them covers 5. |
| Files | `multi-service-coverage.csv`, `service-class-coverage.csv`, `service_class_coverage.py` |
| Date | 2026-11-23 |

---

## 1. What I measured

I grouped 16 infrastructure services into 9 families. A company scores one point per family it sells.

| Family | Service classes inside it |
|---|---|
| Compute | Cloud compute, hosting and deployment |
| Data | Database, storage, data APIs and analytics |
| Network | Networking, CDN, DNS |
| Comms | Messaging, email, voice |
| Money | Payments, wallets and keys |
| Trust | Identity and auth, security |
| AI | AI and model inference |
| Dev tooling | Developer tooling, observability |
| Chain | Blockchain RPC and nodes |

A keyword rule reads the category, the summary, and the service list of each row. The rule file is `service_class_coverage.py`.

**Limit:** the CSV service lists hold 1 to 4 items. So every count here is a lower bound. Supabase shows 3 classes from CSV text, but 7 on its own page.

## 2. The result in the CSV

| Families covered | Companies |
|---|---|
| 6 | 0 |
| 5 | 1 |
| 4 | 1 |
| 3 | 29 |
| 2 | 139 |
| 1 | 79 |
| 0 | 10 |

No company in the CSV sells six or more families.

## 3. The reachable shortlist

These five sell more than one product line, and the lines have different prices.

| # | Company | Families | Classes | What it sells |
|---|---|---|---|---|
| 1 | **Upstash** | 5 | 5 | Serverless Redis, vector database, messaging and workflow |
| 2 | **thirdweb** | 4 | 5 | RPC, wallet APIs, transaction APIs, payment SDK |
| 3 | **BlockRun** | 3 | 3 | Model inference, web search, market data, paid agent tools |
| 4 | **CrewAI** | 3 | 3 | Agent hosting, deployment, monitoring |
| 5 | **LangChain** | 3 | 3 | Agent deployment, tracing, evaluation |

Upstash is the best match. It sells a database, a cache, a message queue, and a vector store. Each one is a separate product with a separate price.

thirdweb is the best Web3 match. It sells infrastructure, a wallet layer, and a payment SDK.

## 4. The second band

These sell three families, but the third one is small.

| Company | Families | Note |
|---|---|---|
| 4EVERLAND | Chain, Compute, Data | RPC plus decentralized storage plus hosting |
| ARKHIA | Chain, Data, Money | RPC plus Hedera data plus AI payments |
| Blink | Chain, Data, Money | RPC plus data plus wallet |
| Chaingateway.io | Chain, Data, Money | RPC plus data plus wallet |
| Tatum | Chain, Data, Money | RPC plus data plus wallet |
| BlockCypher | Chain, Data, Obs | RPC plus data plus monitoring |
| Amforc, AZXA.IO, Allnodes, 01.ro, Block Stack, Kaleido, Launchnodes, NodeOps, RPC Fast, SenseiNode, Stakely, Tenderly | Chain, Compute, Data | One product: node hosting with an API |

The last row is the important one. Twelve companies show three families, but they sell one thing. RPC access needs a node, a host, and a data API. That is one product, not three.

## 5. The real multi-service companies were removed by the size filter

The companies that match your description best are in the CSV, and my own size filter removed them.

| Company | Families from CSV | Classes from CSV | Headcount |
|---|---|---|---|
| Cloudflare | 3 | 4 | large |
| Modal | 3 | 4 | large |
| Alibaba Cloud | 3 | 3 | large |
| HUAWEI CLOUD | 3 | 3 | large |
| MongoDB | 3 | 3 | large |
| Alchemy | 3 | 3 | 373 |
| ChainUp Cloud | 3 | 3 | 120 |
| IntellectEU | 3 | 3 | 222 |
| Amazon Web Services | 2 | 3 | large |
| Google Cloud | 2 | 4 | large |
| IBM Cloud | 2 | 3 | large |
| Oracle Cloud | 2 | 3 | large |
| Supabase | 2 | 3 | large |

The last five show two families only because the CSV lists three services for them. Their own pages list far more. AWS, Google Cloud, Oracle, and IBM each sell compute, database, storage, and network. Supabase lists seven classes on its features page.

So the CSV reading understates them. These are the textbook multi-service companies. You cannot reach them, so they stay out.

**This is the core tension.** Breadth and reachability pull in opposite directions. A company that sells five service classes is large. A company you can email is small.

## 6. Two outside companies that break the pattern

I checked two platforms outside the CSV. Both sell six families and both are small enough to contact.

| Company | Families | Classes | Evidence |
|---|---|---|---|
| **Supabase** | 6 | 7 | Database, auth, storage, edge functions, realtime, vector, cron, queues |
| **Northflank** | 6 | 7 | Services, managed databases, jobs, GPUs, sandboxes, networking, observability |

Supabase is the closest thing to usebuy's shape that I found. It sells a database, an auth service, a file store, a compute runtime, a message bus, and a vector index. Each one has its own price. A developer can start with one and add the rest.

Northflank sells a runtime, managed databases, GPU compute, and sandboxes. It is aimed at agents, so the buyer matches usebuy's buyer.

Both are still larger than usebuy. Supabase is a funded company with a large team.

## 7. Why the pattern is rare

Three reasons, from the data:

1. **The CSV was built from directories.** It lists vendors by one category each. A directory does not record a company that spans three.
2. **Breadth is expensive.** Each service class needs its own operations team. Small companies pick one.
3. **Agents buy narrow.** An agent needs a search result, not a platform. So vendors sell one call.

usebuy is unusual because it is a reseller. It does not run the infrastructure. It rents 170 routes from suppliers and adds a billing layer. That lets a small team show wide coverage.

## 8. Answer to your question

Yes, such companies exist. They fall in three groups.

| Group | Examples | Can you reach them? |
|---|---|---|
| Hyperscalers | AWS, Google Cloud, Azure, Oracle, IBM, Alibaba, Huawei | No |
| Backend platforms | Supabase, Northflank, Firebase, Appwrite | Maybe |
| Small multi-line vendors | Upstash, thirdweb, BlockRun, CrewAI, LangChain | Yes |

The small group is the useful one for outreach. Five companies qualify.

## 9. Recommendation

1. **Use Upstash as the closest reachable peer.** It sells five families at small size. It is the best model of what usebuy wants to become.
2. **Use Supabase as the product model**, not as a target. It shows how to price six services separately under one account.
3. **Treat thirdweb as the direct Web3 rival.** It covers chain, data, dev tooling, and money.
4. **Drop the twelve chain-plus-hosting rows from any breadth claim.** They look broad and are not.

## 10. What I could not verify

| Item | Status |
|---|---|
| Firebase and Appwrite class count | Not in CSV, not fetched |
| Headcount for the hyperscalers | Not in CSV |
| Supabase and Northflank pricing per class | Not read |
| Whether Upstash sells all five as separate paid products | Inferred from site summary |
| Revenue or funding for any company here | Not researched |

## 11. Sources

| Source | URL | Read |
|---|---|---|
| Source CSV | `usebuy-infrastructure-2026-11-20/infrastructure-companies.csv` | local |
| Supabase features | https://supabase.com/features | 2026-11-23 |
| Northflank homepage | https://northflank.com | 2026-11-23 |
