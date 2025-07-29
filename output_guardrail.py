from pydantic import BaseModel, Field
from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunConfig,
    enable_verbose_stdout_logging
)
import os
from dotenv import load_dotenv  
import rich 
from typing import Any

load_dotenv()
enable_verbose_stdout_logging()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

class President_Check_Class(BaseModel):
    is_president: bool = Field(description="insert True if the user is asking about president.")

guardrail_agent = Agent(
    name="guardrail_agent",
    instructions="always check if user is asking about president or not.",
    output_type=President_Check_Class  # <-- Pass the class, not an instance
)

@output_guardrail
async def president_check(
    ctx: RunContextWrapper, agent: Agent, output: Any
) -> GuardrailFunctionOutput:
    guardrail_result = await Runner.run(guardrail_agent,output,context=ctx,run_config=config)
    return GuardrailFunctionOutput(
        output_info=guardrail_result.final_output,
        tripwire_triggered=guardrail_result.final_output.is_president
    )

second_agent = Agent(
    name="second_agent",
    instructions="if the user is asking about president also tell him additionaly about the prime minister.",
    output_guardrails=[president_check]
)

agent = Agent(
    name="triage_agent",
    instructions="You are a helpful assistant.",
    output_guardrails=[president_check],
    handoffs=[second_agent]
)
try:
        result =  Runner.run_sync(agent, input="who is the President of Pakistan in 2023?, delegate to second agent", run_config=config)
        rich.print(result.final_output)

except OutputGuardrailTripwireTriggered as e:
        rich.print("❌",e)