# Company profile: usebuy.ai ("buy")

| Field | Value |
|---|---|
| Company / product | usebuy.ai, product name **buy** |
| Category | Agentic commerce. Pay-per-request service marketplace. |
| Chain | Celo mainnet (chain ID 42220), test on Celo Sepolia (11142220) |
| Protocol | x402 (HTTP 402), v1 and v2 |
| Release | v0.8.7 (site), v0.8.6 (npm latest), beta, pre-1.0 |
| Licence | Apache-2.0 |
| Domain created | 2026-08-27 |
| First npm publish | 2026-08-25 |
| Version count | 17 |
| Catalogue | 782 tools (site, 2026-10-13), 170 capabilities on the gateway API |
| Price range | $0.0036 to $12.003 per call |
| Package | `@celo/buy` |
| Profile date | 2026-11-23 |

This profile uses primary sources only: the product site, the docs, the limits page, the live gateway catalogue, the npm registry, GitHub, and WHOIS. Section 11 lists the open gaps.

---

## 1. One-line summary

buy lets an AI agent pay for one HTTP request with one stablecoin transfer on Celo. There is no account, no API key, and no subscription. The agent reads a 402 quote, signs a transfer, and gets the result.

## 2. What the product does

An agent sends a normal HTTP request. The server answers `402 Payment Required` with a price. The `buy` CLI signs an EIP-3009 stablecoin transfer with a key in the OS keychain. It retries the same request with an `X-PAYMENT` header. The server verifies the signature, settles on Celo, and returns the answer.

The value claim is simple. A developer connects an agent to paid data and compute without a billing integration, a credit card, or a vendor account.

Three install paths exist:

1. CLI: `npm install -g @celo/buy@0.8.7`
2. MCP server: `buy mcp install --client all`, for Claude Code and Codex
3. Sandbox: `--sandbox` flag, which pays with test USDC on Celo Sepolia

The MCP server registers eight tools. Seven are on by default. `buy_send`, the one tool that moves money, stays opt-in behind a budget or an allowlist.

## 3. Architecture

| Layer | What it is | Evidence |
|---|---|---|
| Client | `buy` CLI and MCP server. Wallet in the OS keychain. | npm package, docs |
| Gateway | `gateway.usebuy.ai`. Quotes each request, verifies payment, proxies upstream. | `/v1/catalog` |
| Facilitator | `@celo/buy-facilitator`. Verifies and settles x402 payments. | npm dependencies |
| Registry | `@celo/buy-registry`, ERC-8004 identity and reputation registries on Celo. | `/v1/catalog` trust block |
| Identity | `@celo/buy-identity`, Self.xyz zero-knowledge proofs. | docs, "Verify with Self" |

The npm package is split into eight sub-packages: `buy-core`, `buy-gateway`, `buy-mcp`, `buy-identity`, `buy-keystore`, `buy-registry`, `buy-facilitator`, and the CLI. This is a full payments stack, not a thin wrapper.

## 4. Catalogue composition

The homepage claims 782 tools. The gateway API returns 170 capabilities, of which 149 are available and 21 are not. The gap is explained by Agent402. The site links many tools to `agent402.tools`, which advertises "500+ tools on the same rails". So the 782 figure is a combined count, not 782 first-party services.

Gateway capabilities by platform:

| Platform | Capabilities |
|---|---|
| Instagram | 35 |
| TikTok | 32 |
| YouTube | 32 |
| LinkedIn | 25 |
| Reddit | 22 |
| X | 19 |
| Flights | 2 |
| Browser | 1 |
| Chainstack RPC | 1 |
| Cencori inference | 1 |

Gateway capabilities by upstream provider:

| Provider | Capabilities |
|---|---|
| TikHub | 121 |
| Apify | 27 |
| MrScraper | 7 |
| Ploid | 6 |
| Strale | 2 |
| ContactOut | 2 |
| Clay | 1 |
| Kadec0 | 1 |
| First-party browser worker | 1 |

**Key finding.** 71% of the gateway catalogue is resold TikHub social-media scraping. The social data category is the core revenue surface. Compute, blockchain, and browser are small side routes.

## 5. Pricing and unit economics

| Route | Price |
|---|---|
| Gateway capabilities | $0.0036 to $12.003 per call. 73 listed price points. Median $0.025. |
| Google Cloud VM, `e2-micro` | $0.0168 per hour |
| Google Cloud VM, `e2-standard-8` | $0.5361 per hour |
| Chainstack Celo RPC | $0.01 per request |
| Cencori inference | $0.01 per completion |
| SQD Portal multi-chain data | Free, rate limited |

Payment tokens: USDC (default), USD₮, and USA₮. All settle on Celo. The gateway sponsors gas, so a wallet needs no CELO.

The revenue model is not published. The evidence points to a resale margin on third-party scrapers, a margin on the two partner routes, and a margin on Google Cloud VM resale. There is no subscription tier and no stated take rate. Treat this as inference, not fact.

## 6. Trust, identity, and compliance

This is the most differentiated part of the product.

- **ERC-8004 registries.** The catalogue exposes identity and reputation registries on Celo. Payer feedback travels in an `X-8004-Agent-Id` header.
- **Self.xyz proofs.** Some endpoints demand proof of a real person: age 18 or over, and not on a sanctions list. The proof is zero-knowledge, built from a passport in the Self app, and bound to the paying wallet. Scope is `buy.celo`.
- **Two price tiers of access.** Shared-core VMs need no proof. `e2-standard` sizes need the Self proof. The product sells identity-gated compute, not only payments.
- **Google Cloud faucet.** Google Cloud runs a mainnet USA₮ faucet for Celo, gated by the same Self proof. This ties the product to a Google Cloud and Celo go-to-market motion.

## 7. Limits and safety posture

The product publishes hard caps. This is a positive signal for a beta.

| Cap | Value |
|---|---|
| VMs at once, fleet-wide | 100 |
| Catalogued compute, fleet-wide | $25 per hour |
| VM lease | 1 hour per purchase |
| VM total life | 24 hours |
| Network egress per VM | 10 GB, then the VM is deleted with no refund |
| Payment validity window | 300 seconds |
| Whole request | 12 minutes |
| JSON body | 64 KiB |
| Free SQD route | 120 requests per minute per IP |

Stated risks: beta software, no external security review, payments are final, and no refunds. The docs say it is "not intended for production use".

## 8. Team and ownership signals

| Signal | Finding |
|---|---|
| npm scope | `@celo` |
| npm maintainer emails | `@clabs.co` (three named maintainers plus an `app-tooling` account) |
| GitHub organisation | `celo-org` (repo `celo-org/buy-skill`) |
| Related cLabs repo | `celo-org/mpp`, the Machine Payments Protocol site |
| Domain registrar | Cloudflare, registrant country US, details redacted |
| Hosting | Google front-end addresses, Cloudflare DNS |

**Inference.** buy is a Celo Labs (cLabs) project, built inside the Celo ecosystem. The product name, the package scope, the maintainer emails, and the repo all point one way. No legal entity, no funding round, and no headcount are public. Do not state a company size.

## 9. Timeline

| Date | Event |
|---|---|
| 2026-08-25 | First npm publish |
| 2026-08-27 | Domain registered |
| 2026-10-13 | Catalogue prices captured for the site snapshot |
| 2026-11-18 | npm package last modified |
| 2026-11-19 | `buy-skill` repo last pushed |
| 2026-11-23 | This profile. Site at v0.8.7. |

The product is about three months old. It shipped 17 npm versions in that time. Release speed is high and scope is still moving.

## 10. How this connects to the infrastructure list

The 259-vendor CSV in `outputs/usebuy-infrastructure-2026-11-20/` is a map of the supply side that buy sells. The overlap is direct:

| CSV category | buy already uses |
|---|---|
| Blockchain RPC and data APIs | Chainstack, SQD |
| Cloud compute | Google Cloud |
| Model inference | Cencori, Agent402 LLM gateway |
| Web data infrastructure | TikHub, Apify, MrScraper, Ploid, ContactOut, Clay, Strale, Kadec0 |
| Browser infrastructure | First-party browser worker |
| Identity infrastructure | Self.xyz |

Categories in the CSV that buy does not yet sell:

- Agent memory (Mem0, Zep)
- Agent observability and evaluation (LangChain, AgentOps, HoneyHive)
- Code execution sandboxes (E2B, Modal)
- Email and voice infrastructure (Resend, AgentMail, Deepgram, Telnyx)
- Workflow infrastructure (Inngest, Hatchet)
- Vector and database infrastructure (Pinecone, Neon, Supabase)

That list is the natural expansion path, and the natural opening for a vendor conversation.

## 11. Gaps and open questions

1. **No legal entity, address, or headcount.** WHOIS is redacted. No About page, no team page, no blog.
2. **No funding or investor data.** Nothing public.
3. **No published take rate.** The margin on resold scrapers is unknown.
4. **Catalogue count is ambiguous.** 782 claimed, 170 on the gateway, 149 available.
5. **No usage or volume data.** No transaction counts, no GMV, no active wallet counts.
6. **No customer names.** No case studies.
7. **Version mismatch.** Site says v0.8.7. npm latest is v0.8.6.
8. **Security posture is self-declared.** No external audit exists.
9. **No status page.** No uptime record.

## 12. Suggested next actions

1. Confirm the legal entity and the cLabs relationship before any contract talk.
2. Ask for the take rate on resold routes.
3. Ask which catalogue categories are growing and which are flat.
4. Ask if the roadmap includes memory, sandboxes, or observability. Those are the CSV categories it lacks.
5. Check the 21 unavailable capabilities. They show what broke or what is being rebuilt.

## 13. Sources

| Source | URL | Read on |
|---|---|---|
| Product site | https://usebuy.ai | 2026-11-23 |
| Docs | https://usebuy.ai/docs | 2026-11-23 |
| Limits | https://usebuy.ai/limits | 2026-11-23 |
| Gateway catalogue | https://gateway.usebuy.ai/v1/catalog | 2026-11-23 |
| npm registry | https://registry.npmjs.org/@celo%2Fbuy | 2026-11-23 |
| GitHub | https://github.com/celo-org/buy-skill | 2026-11-23 |
| Agent402 | https://agent402.tools | 2026-11-23 |
| WHOIS | whois.nic.ai | 2026-11-23 |
| DNS | Cloudflare NS, Google A records | 2026-11-23 |

All figures above come from these sources. Items marked as inference are not sourced.
