// Chairman-driven session orchestrator skeleton.
// Loads agent cards, opens sessions, routes progress reports.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Deserialize, Serialize, Clone)]
struct AgentCard {
    id: String,
    display_name: String,
    role: String,
    reacts_to: Vec<String>,
}

#[derive(Debug, Deserialize, Serialize)]
struct Session {
    id: String,
    task: String,
    agents: Vec<String>,
    status: String,
}

fn main() {
    println!("zenos-council: Chairman session orchestrator (skeleton)");
    // TODO: load dex/agents/*.json, open session, route reports
}
