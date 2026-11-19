use async_trait::async_trait;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Reply {
    pub text: String,
}

#[async_trait]
pub trait AgentProvider: Send + Sync {
    async fn send(&self, prompt: &str) -> Result<Reply, String>;
}

pub struct GrokBotProvider {
    pub agent_id: String,
}

#[async_trait]
impl AgentProvider for GrokBotProvider {
    async fn send(&self, prompt: &str) -> Result<Reply, String> {
        // TODO: call bot_send_prompt + bot_await_turn or HTTP bridge
        Ok(Reply {
            text: format!("[grok:{}] stub reply to: {}", self.agent_id, prompt),
        })
    }
}
