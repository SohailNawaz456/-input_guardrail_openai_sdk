from pydantic import BaseModel, Field
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunConfig,
    enable_verbose_stdout_logging
)
import os
from dotenv import load_dotenv 
import asyncio  
import rich 

# Load environment variables from .env file
load_dotenv()

# Optional: enable detailed logging for debugging
# enable_verbose_stdout_logging()

# Get the Gemini API key from environment variables
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Raise error if API key is not set
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

# Configure external OpenAI-compatible Gemini client
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Define the chat model using Gemini 2.0 Flash
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

# Set up run configuration
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

# Define the structure of the guardrail's output
class Prime_Minister_Check(BaseModel):
    is_prime_minister: bool = Field(description="If user is asking about the prime minister, set this to True.")

# Agent that checks if the user is asking about the prime minister
guardrail_agent = Agent(
    name="Guardrail_agent",
    instructions="You check if the user is asking about prime minister or not.",
    output_type=Prime_Minister_Check,
)

# Guardrail function to check the input
@input_guardrail
async def prime_minister_check(
    ctx: RunContextWrapper, agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    # Run the guardrail agent on the input
    guardrail_result = await Runner.run(guardrail_agent, input, context=ctx.context, run_config=config)

    # Return whether a tripwire (trigger condition) is met
    return GuardrailFunctionOutput(
        output_info=guardrail_result.final_output,
        tripwire_triggered=guardrail_result.final_output.is_prime_minister,
    )

second_agent = Agent(
    name="second_agent",
    instructions="if user is asking about the president ,so additionaly tell about prime minister and reply to user",  
    input_guardrails=[prime_minister_check],
    handoff_description="you tell user about presdient and prime minister"                                                                                        
)

# Main agent that handles general queries but has input guardrails
agent = Agent(
    name="triage_agent",
    instructions="You are a helpful assistant.",
    input_guardrails=[prime_minister_check],
    handoffs=[second_agent],
)

# Main function to run the agent and handle guardrail trips
# Main function to run the agent and handle guardrail trips
async def main():
    try:
        # Test input — change this to test different queries
        result = await Runner.run(agent, "Hi, tell me who is the president of Pakistan, call second agent", run_config=config)

        # If successful, show checkmark and output
        rich.print("✅ Guardrail unexpected:", result.final_output)

    # If guardrail is triggered
    except InputGuardrailTripwireTriggered:
        rich.print("❌ Guardrail triggered: Prime Minister-related query detected. Blocking input.")

# Run the main function if script is executed
if __name__ == "__main__":
    asyncio.run(main())
