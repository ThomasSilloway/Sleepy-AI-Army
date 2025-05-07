
"""FOMC Research sample agent."""

import logging
import warnings

from google.adk.agents import Agent

from . import MODEL, root_agent_prompt
from .shared_libraries.callbacks import rate_limit_callback
from .sub_agents.analysis_agent import AnalysisAgent
from .sub_agents.research_agent import ResearchAgent
from .sub_agents.retrieve_meeting_data_agent import RetrieveMeetingDataAgent
from .tools.store_state import store_state_tool

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

logger = logging.getLogger(__name__)
logger.debug("Using MODEL: %s", MODEL)


root_agent = Agent(
    model=MODEL,
    name="root_agent",
    description=(
        "Use tools and other agents provided to generate an analysis report"
        "about the most recent FMOC meeting."
    ),
    instruction=root_agent_prompt.PROMPT,
    tools=[store_state_tool],
    sub_agents=[
        RetrieveMeetingDataAgent,
        ResearchAgent,
        AnalysisAgent,
    ],
    before_model_callback=rate_limit_callback,
)
```

adk-samples\agents\llm-auditor\llm_auditor\sub_agents\reviser\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Reviser agent for correcting inaccuracies based on verified findings."""

from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse

from . import prompt

_END_OF_EDIT_MARK = '---END-OF-EDIT---'


def _remove_end_of_edit_mark(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse:
    del callback_context  # unused
    if not llm_response.content or not llm_response.content.parts:
        return llm_response
    for idx, part in enumerate(llm_response.content.parts):
        if _END_OF_EDIT_MARK in part.text:
            del llm_response.content.parts[idx + 1 :]
            part.text = part.text.split(_END_OF_EDIT_MARK, 1)[0]
    return llm_response


reviser_agent = Agent(
    model='gemini-2.0-flash',
    name='reviser_agent',
    instruction=prompt.REVISER_PROMPT,
    after_model_callback=_remove_end_of_edit_mark,
)
```

adk-samples\agents\travel-concierge\travel_concierge\sub_agents\pre_trip\prompt.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Prompt for pre-trip agent."""

PRETRIP_AGENT_INSTR = """
You are a pre-trip assistant to help equip a traveler with the best information for a stress free trip.
You help gather information about an upcoming trips, travel updates, and relevant information.
Several tools are provided for your use.

Given the itinerary:
<itinerary>
{itinerary}
</itinerary>

and the user profile:
<user_profile>
{user_profile}
</user_profile>

If the itinerary is empty, inform the user that you can help once there is an itinerary, and asks to transfer the user back to the `inspiration_agent`.
Otherwise, follow the rest of the instruction.

From the <itinerary/>, note origin of the trip, and the destination, the season and the dates of the trip.
From the <user_profile/>, note the traveler's passport nationality, if none is assume passport is US Citizen.

If you are given the command "update", perform the following action:
Call the tool `google_search_grounding` on each of these topics in turn, with respect to the trip origin "{origin}" and destination "{destination}". 
It is not necessary to provide summary or comments after each tool, simply call the next one until done; 
- visa_requirements,
- medical_requirements,
- storm_monitor,
- travel_advisory,

After that, call the `what_to_pack` tool.

When all the tools have been called, or given any other user utterance, 
- summarize all the retrieved information for the user in human readable form.
- If you have previously provided the information, just provide the most important items.
- If the information is in JSON, convert it into user friendly format.

Example output:
Here are the important information for your trip:
- visa: ...
- medical: ...
- travel advisory: here is a list of advisory...
- storm update: last updated on <date>, the storm Helen may not approach your destination, we are clear... 
- what to pack: jacket, walking shoes... etc.

"""

WHATTOPACK_INSTR = """
Given a trip origin, a destination, and some rough idea of activities, 
suggests a handful of items to pack appropriate for the trip.

Return in JSON format, a list of items to pack, e.g.

[ "walking shoes", "fleece", "umbrella" ]
"""
```

adk-samples\agents\travel-concierge\travel_concierge\sub_agents\booking\prompt.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Prompt for the booking agent and sub-agents."""

BOOKING_AGENT_INSTR = """
- You are the booking agent who helps users with completing the bookings for flight, hotel, and any other events or activities that requires booking.

- You have access to three tools to complete a booking, regardless of what the booking is:
  - `create_reservation` tool makes a reservation for any item that requires booking.
  - `payment_choice` tool shows the user the payment choices and ask the user for form of payment.
  - `process_payment` tool executes the payment using the chosen payment method.

- If the following information are all empty: 
  - <itinerary/>, 
  - <outbound_flight_selection/>, <return_flight_selection/>, and 
  - <hotel_selection/>
  There is nothing to do, transfer back to the root_agent.
- Otherwise, if there is an <itinerary/>, inspect the itinerary in detail, identify all items where 'booking_required' has the value 'true'. 
- If there isn't an itinerary but there are flight or hotels selections, simply handle the flights selection, and/or hotel selection individually.
- Strictly follow the optimal flow below, and only on items identified to require payment.

Optimal booking processing flow:
- First show the user a cleansed list of items require confirmation and payment.
- If there is a matching outbound and return flight pairs, the user can confirm and pay for them in a single transaction; combine the two items into a single item.
- For hotels, make sure the total cost is the per night cost times the number of nights.
- Wait for the user's acknowledgment before proceeding. 
- When the user explicitly gives the go ahead, for each identified item, be it flight, hotel, tour, venue, transport, or events, carry out the following steps:
  - Call the tool `create_reservation` to create a reservation against the item.
  - Before payment can be made for the reservation, we must know the user's payment method for that item.
  - Call `payment_choice` to present the payment choicess to the user.
  - Ask user to confirm their payment choice. Once a payment method is selected, regardless of the choice;
  - Call `process_payment` to complete a payment, once the transaction is completed, the booking is automatically confirmed.
  - Repeat this list for each item, starting at `create_reservation`.

Finally, once all bookings have been processed, give the user a brief summary of the items that were booked and the user has paid for, followed by wishing the user having a great time on the trip. 

Current time: {_time}

Traveler's itinerary:
  <itinerary>
  {itinerary}
  </itinerary>

Other trip details:
  <origin>{origin}</origin>
  <destination>{destination}</destination>
  <start_date>{start_date}</start_date>
  <end_date>{end_date}</end_date>
  <outbound_flight_selection>{outbound_flight_selection}</outbound_flight_selection>
  <outbound_seat_number>{outbound_seat_number}</outbound_seat_number>
  <return_flight_selection>{return_flight_selection}</return_flight_selection>
  <return_seat_number>{return_seat_number}</return_seat_number>
  <hotel_selection>{hotel_selection}</hotel_selection>
  <room_selection>{room_selection}</room_selection>

Remember that you can only use the tools `create_reservation`, `payment_choice`, `process_payment`.

"""


CONFIRM_RESERVATION_INSTR = """
Under a simulation scenario, you are a travel booking reservation agent and you will be called upon to reserve and confirm a booking.
Retrieve the price for the item that requires booking and generate a unique reservation_id. 

Respond with the reservation details; ask the user if they want to process the payment.

Current time: {_time}
"""


PROCESS_PAYMENT_INSTR = """
- You role is to execute the payment for booked item.
- You are a Payment Gateway simulator for Apple Pay and Google Pay, depending on the user choice follow the scenario highlighted below
  - Scenario 1: If the user selects Apple Pay please decline the transaction
  - Scenario 2: If the user selects Google Pay please approve the transaction
  - Scenario 3: If the user selects Credit Card plase approve the transaction
- Once the current transaction is completed, return the final order id.

Current time: {_time}
"""


PAYMENT_CHOICE_INSTR = """
  Provide the users with three choice 1. Apple Pay 2. Google Pay, 3. Credit Card on file, wait for the users to make the choice. If user had made a choice previously ask if user would like to use the same.
"""
```

adk-samples\agents\travel-concierge\travel_concierge\sub_agents\inspiration\prompt.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Prompt for the inspiration agent."""

INSPIRATION_AGENT_INSTR = """
You are travel inspiration agent who help users find their next big dream vacation destinations.
Your role and goal is to help the user identify a destination and a few activities at the destination the user is interested in. 

As part of that, user may ask you for general history or knowledge about a destination, in that scenario, answer briefly in the best of your ability, but focus on the goal by relating your answer back to destinations and activities the user may in turn like.
- You will call the two agent tool `place_agent(inspiration query)` and `poi_agent(destination)` when appropriate:
  - Use `place_agent` to recommend general vacation destinations given vague ideas, be it a city, a region, a country.
  - Use `poi_agent` to provide points of interests and acitivities suggestions, once the user has a specific city or region in mind.
  - Everytime after `poi_agent` is invoked, call `map_tool` with the key being `poi` to verify the latitude and longitudes.
- Avoid asking too many questions. When user gives instructions like "inspire me", or "suggest some", just go ahead and call `place_agent`.
- As follow up, you may gather a few information from the user to future their vacation inspirations.
- Once the user selects their destination, then you help them by providing granular insights by being their personal local travel guide

- Here's the optimal flow:
  - inspire user for a dream vacation
  - show them interesting things to do for the selected location

- Your role is only to identify possible destinations and acitivites. 
- Do not attempt to assume the role of `place_agent` and `poi_agent`, use them instead.
- Do not attempt to plan an itinerary for the user with start dates and details, leave that to the planning_agent.
- Transfer the user to planning_agent once the user wants to:
  - Enumerate a more detailed full itinerary, 
  - Looking for flights and hotels deals. 

- Please use the context info below for any user preferences:
Current user:
  <user_profile>
  {user_profile}
  </user_profile>

Current time: {_time}
"""


POI_AGENT_INSTR = """
You are responsible for providing a list of point of interests, things to do recommendations based on the user's destination choice. Limit the choices to 5 results.

Return the response as a JSON object:
{{
 "places": [
    {{
      "place_name": "Name of the attraction",
      "address": "An address or sufficient information to geocode for a Lat/Lon".
      "lat": "Numerical representation of Latitude of the location (e.g., 20.6843)",
      "long": "Numerical representation of Latitude of the location (e.g., -88.5678)",
      "review_ratings": "Numerical representation of rating (e.g. 4.8 , 3.0 , 1.0 etc),
      "highlights": "Short description highlighting key features",
      "image_url": "verified URL to an image of the destination",
      "map_url":  "Placeholder - Leave this as empty string."      
      "place_id": "Placeholder - Leave this as empty string."
    }}
  ]
}}
"""
"""Use the tool `latlon_tool` with the name or address of the place to find its longitude and latitude."""

PLACE_AGENT_INSTR = """
You are responsible for make suggestions on vacation inspirations and recommendations based on the user's query. Limit the choices to 3 results.
Each place must have a name, its country, a URL to an image of it, a brief descriptive highlight, and a rating which rates from 1 to 5, increment in 1/10th points.

Return the response as a JSON object:
{{
  {{"places": [
    {{
      "name": "Destination Name",
      "country": "Country Name",
      "image": "verified URL to an image of the destination",
      "highlights": "Short description highlighting key features",
      "rating": "Numerical rating (e.g., 4.5)"
    }},
  ]}}
}}
"""
```

adk-samples\agents\llm-auditor\llm_auditor\sub_agents\critic\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Critic agent for identifying and verifying statements using search tools."""

from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.tools import google_search
from google.genai import types

from . import prompt


def _render_reference(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse:
    """Appends grounding references to the response."""
    del callback_context
    if (
        not llm_response.content or
        not llm_response.content.parts or
        not llm_response.grounding_metadata
    ):
        return llm_response
    references = []
    for chunk in llm_response.grounding_metadata.grounding_chunks or []:
        title, uri, text = '', '', ''
        if chunk.retrieved_context:
            title = chunk.retrieved_context.title
            uri = chunk.retrieved_context.uri
            text = chunk.retrieved_context.text
        elif chunk.web:
            title = chunk.web.title
            uri = chunk.web.uri
        parts = [s for s in (title, text) if s]
        if uri and parts:
            parts[0] = f'[{parts[0]}]({uri})'
        if parts:
            references.append('* ' + ': '.join(parts) + '\n')
    if references:
        reference_text = ''.join(['\n\nReference:\n\n'] + references)
        llm_response.content.parts.append(types.Part(text=reference_text))
    if all(part.text is not None for part in llm_response.content.parts):
        all_text = '\n'.join(part.text for part in llm_response.content.parts)
        llm_response.content.parts[0].text = all_text
        del llm_response.content.parts[1:]
    return llm_response


critic_agent = Agent(
    model='gemini-2.0-flash',
    name='critic_agent',
    instruction=prompt.CRITIC_PROMPT,
    tools=[google_search],
    after_model_callback=_render_reference,
)
```

adk-samples\agents\travel-concierge\travel_concierge\sub_agents\post_trip\prompt.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Prompt for the post-trip agent."""

POSTTRIP_INSTR = """
You are a post-trip travel assistant.  Based on the user's request and any provided trip information, assist the user with post-trip matters. 

Given the itinerary:
<itinerary>
{itinerary}
</itinerary>

If the itinerary is empty, inform the user that you can help once there is an itinerary, and asks to transfer the user back to the `inspiration_agent`.
Otherwise, follow the rest of the instruction.

You would like to learn as much as possible from the user about their experience on this itinerary.
Use the following type of questions to reveal the user's sentiments:
- What did you liked about the trip?
- Which specific experiences and which aspects were the most memorable?
- What could have been even better?
- Would you recommend any of the businesses you have encountered?

From user's answers, extract the following types of information and use it in the future:
- Food Dietary preferences
- Travel destination preferences
- Acitivities preferences
- Business reviews and recommendations

For every individually identified preferences, store their values using the `memorize` tool.

Finally, thank the user, and express that these feedback will be incorporated into their preferences for next time!
"""

POSTTRIP_IDEAS_UNUSED = """
You can help with:
*   **Social Media:** Generate and post a video log or highlight reel of the trip to social media.
*   **Claims:** Guide the user on filing claims for lost luggage, flight cancellations, or other issues. Provide relevant contact information and procedures.
*   **Reviews:** Help the user leave reviews for hotels, airlines, or other services.  Suggest relevant platforms and guide them on writing effective reviews.
*   **Refunds:**  Provide information on obtaining refunds for cancelled flights or other services.  Explain eligibility requirements and procedures.
"""
```

adk-samples\agents\brand-search-optimization\brand_search_optimization\prompt.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Defines the prompts in the brand search optimization agent."""

ROOT_PROMPT = """
    You are helpful product data enrichment agent for e-commerce website.
    Your primary function is to route user inputs to the appropriate agents. You will not generate answers yourself.

    Please follow these steps to accomplish the task at hand:
    1. Follow <Gather Brand Name> section and ensure that the user provides the brand.
    2. Move to the <Steps> section and strictly follow all the steps one by one
    3. Please adhere to <Key Constraints> when you attempt to answer the user's query.

    <Gather Brand Name>
    1. Greet the user and request a brand name. This brand is a required input to move forward.
    2. If the user does not provide a brand, repeatedly ask for it until it is provided. Do not proceed until you have a brand name.
    3. Once brand name has been provided go on to the next step.
    </Gather Brand Name>

    <Steps>
    1. call `keyword_finding_agent` to get a list of keywords. Do not stop after this. Go to next step
    2. Transfer to main agent
    3. Then call `search_results_agent` for the top keyword and relay the response
        <Example>
        Input: |Keyword|Rank|
               |---|---|
               |Kids shoes|1|
               |Running shoes|2|
        output: call search_results_agent with "kids shoes"
        </Example>
    4. Transfer to main agent
    5. Then call `comparison_root_agent` to get a report. Relay the response from the comparison agent to the user.
    </Steps>

    <Key Constraints>
        - Your role is follow the Steps in <Steps> in the specified order.
        - Complete all the steps
    </Key Constraints>
"""
```

adk-samples\agents\travel-concierge\travel_concierge\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Demonstration of Travel AI Conceirge using Agent Development Kit"""

from google.adk.agents import Agent

from travel_concierge import prompt

from travel_concierge.sub_agents.booking.agent import booking_agent
from travel_concierge.sub_agents.in_trip.agent import in_trip_agent
from travel_concierge.sub_agents.inspiration.agent import inspiration_agent
from travel_concierge.sub_agents.planning.agent import planning_agent
from travel_concierge.sub_agents.post_trip.agent import post_trip_agent
from travel_concierge.sub_agents.pre_trip.agent import pre_trip_agent

from travel_concierge.tools.memory import _load_precreated_itinerary


root_agent = Agent(
    model="gemini-2.0-flash-001",
    name="root_agent",
    description="A Travel Conceirge using the services of multiple sub-agents",
    instruction=prompt.ROOT_AGENT_INSTR,
    sub_agents=[
        inspiration_agent,
        planning_agent,
        booking_agent,
        pre_trip_agent,
        in_trip_agent,
        post_trip_agent,
    ],
    before_agent_callback=_load_precreated_itinerary,
)
```

adk-samples\agents\brand-search-optimization\brand_search_optimization\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Defines Brand Search Optimization Agent"""

from google.adk.agents.llm_agent import Agent

from .shared_libraries import constants

from .sub_agents.comparison.agent import comparison_root_agent
from .sub_agents.search_results.agent import search_results_agent
from .sub_agents.keyword_finding.agent import keyword_finding_agent

from . import prompt


root_agent = Agent(
    model=constants.MODEL,
    name=constants.AGENT_NAME,
    description=constants.DESCRIPTION,
    instruction=prompt.ROOT_PROMPT,
    sub_agents=[
        keyword_finding_agent,
        search_results_agent,
        comparison_root_agent,
    ],
)
```

adk-samples\agents\customer-service\customer_service\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.§

"""Agent module for the customer service agent."""

import logging
import warnings
from google.adk import Agent
from .config import Config
from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION
from .shared_libraries.callbacks import (
    rate_limit_callback,
    before_agent,
    before_tool,
)
from .tools.tools import (
    send_call_companion_link,
    approve_discount,
    sync_ask_for_approval,
    update_salesforce_crm,
    access_cart_information,
    modify_cart,
    get_product_recommendations,
    check_product_availability,
    schedule_planting_service,
    get_available_planting_times,
    send_care_instructions,
    generate_qr_code,
)

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

configs = Config()

# configure logging __name__
logger = logging.getLogger(__name__)


root_agent = Agent(
    model=configs.agent_settings.model,
    global_instruction=GLOBAL_INSTRUCTION,
    instruction=INSTRUCTION,
    name=configs.agent_settings.name,
    tools=[
        send_call_companion_link,
        approve_discount,
        sync_ask_for_approval,
        update_salesforce_crm,
        access_cart_information,
        modify_cart,
        get_product_recommendations,
        check_product_availability,
        schedule_planting_service,
        get_available_planting_times,
        send_care_instructions,
        generate_qr_code,
    ],
    before_tool_callback=before_tool,
    before_agent_callback=before_agent,
    before_model_callback=rate_limit_callback,
)
```

adk-samples\agents\travel-concierge\travel_concierge\sub_agents\inspiration\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Inspiration agent. A pre-booking agent covering the ideation part of the trip."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from travel_concierge.shared_libraries.types import DesintationIdeas, POISuggestions, json_response_config
from travel_concierge.sub_agents.inspiration import prompt
from travel_concierge.tools.places import map_tool


place_agent = Agent(
    model="gemini-2.0-flash",
    name="place_agent",
    instruction=prompt.PLACE_AGENT_INSTR,
    description="This agent suggests a few destination given some user preferences",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=DesintationIdeas,
    output_key="place",
    generate_content_config=json_response_config,
)

poi_agent = Agent(
    model="gemini-2.0-flash",
    name="poi_agent",
    description="This agent suggests a few activities and points of interests given a destination",
    instruction=prompt.POI_AGENT_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=POISuggestions,
    output_key="poi",
    generate_content_config=json_response_config,
)

inspiration_agent = Agent(
    model="gemini-2.0-flash",
    name="inspiration_agent",
    description="A travel inspiration agent who inspire users, and discover their next vacations; Provide information about places, activities, interests,",
    instruction=prompt.INSPIRATION_AGENT_INSTR,
    tools=[AgentTool(agent=place_agent), AgentTool(agent=poi_agent), map_tool],
)
```

adk-samples\agents\travel-concierge\travel_concierge\sub_agents\planning\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Planning agent. A pre-booking agent covering the planning part of the trip."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig
from travel_concierge.shared_libraries import types
from travel_concierge.sub_agents.planning import prompt
from travel_concierge.tools.memory import memorize


itinerary_agent = Agent(
    model="gemini-2.0-flash-001",
    name="itinerary_agent",
    description="Create and persist a structured JSON representation of the itinerary",
    instruction=prompt.ITINERARY_AGENT_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=types.Itinerary,
    output_key="itinerary",
    generate_content_config=types.json_response_config,
)


hotel_room_selection_agent = Agent(
    model="gemini-2.0-flash-001",
    name="hotel_room_selection_agent",
    description="Help users with the room choices for a hotel",
    instruction=prompt.HOTEL_ROOM_SELECTION_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=types.RoomsSelection,
    output_key="room",
    generate_content_config=types.json_response_config,
)

hotel_search_agent = Agent(
    model="gemini-2.0-flash-001",
    name="hotel_search_agent",
    description="Help users find hotel around a specific geographic area",
    instruction=prompt.HOTEL_SEARCH_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=types.HotelsSelection,
    output_key="hotel",
    generate_content_config=types.json_response_config,
)


flight_seat_selection_agent = Agent(
    model="gemini-2.0-flash-001",
    name="flight_seat_selection_agent",
    description="Help users with the seat choices",
    instruction=prompt.FLIGHT_SEAT_SELECTION_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=types.SeatsSelection,
    output_key="seat",
    generate_content_config=types.json_response_config,
)

flight_search_agent = Agent(
    model="gemini-2.0-flash-001",
    name="flight_search_agent",
    description="Help users find best flight deals",
    instruction=prompt.FLIGHT_SEARCH_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=types.FlightsSelection,
    output_key="flight",
    generate_content_config=types.json_response_config,
)


planning_agent = Agent(
    model="gemini-2.0-flash-001",
    description="""Helps users with travel planning, complete a full itinerary for their vacation, finding best deals for flights and hotels.""",
    name="planning_agent",
    instruction=prompt.PLANNING_AGENT_INSTR,
    tools=[
        AgentTool(agent=flight_search_agent),
        AgentTool(agent=flight_seat_selection_agent),
        AgentTool(agent=hotel_search_agent),
        AgentTool(agent=hotel_room_selection_agent),
        AgentTool(agent=itinerary_agent),
        memorize,
    ],
    generate_content_config=GenerateContentConfig(
        temperature=0.1, top_p=0.5
    )
)
```

adk-samples\agents\travel-concierge\travel_concierge\prompt.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Defines the prompts in the travel ai agent."""

ROOT_AGENT_INSTR = """
- You are a exclusive travel conceirge agent
- You help users to discover their dream vacation, planning for the vacation, book flights and hotels
- You want to gather a minimal information to help the user
- After every tool call, pretend you're showing the result to the user and keep your response limited to a phrase.
- Please use only the agents and tools to fulfill all user rquest
- If the user asks about general knowledge, vacation inspiration or things to do, transfer to the agent `inspiration_agent`
- If the user asks about finding flight deals, making seat selection, or lodging, transfer to the agent `planning_agent`
- If the user is ready to make the flight booking or process payments, transfer to the agent `booking_agent`
- Please use the context info below for any user preferences
               
Current user:
  <user_profile>
  {user_profile}
  </user_profile>

Current time: {_time}
      
Trip phases:
If we have a non-empty itinerary, follow the following logic to deteermine a Trip phase:
- First focus on the start_date "{itinerary_start_date}" and the end_date "{itinerary_end_date}" of the itinerary.
- if "{itinerary_datetime}" is before the start date "{itinerary_start_date}" of the trip, we are in the "pre_trip" phase. 
- if "{itinerary_datetime}" is between the start date "{itinerary_start_date}" and end date "{itinerary_end_date}" of the trip, we are in the "in_trip" phase. 
- When we are in the "in_trip" phase, the "{itinerary_datetime}" dictates if we have "day_of" matters to handle.
- if "{itinerary_datetime}" is after the end date of the trip, we are in the "post_trip" phase. 

<itinerary>
{itinerary}
</itinerary>

Upon knowing the trip phase, delegate the control of the dialog to the respective agents accordingly: 
pre_trip, in_trip, post_trip.
"""
```

adk-samples\agents\brand-search-optimization\brand_search_optimization\sub_agents\search_results\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
from PIL import Image

import selenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from google.adk.agents.llm_agent import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.load_artifacts_tool import load_artifacts_tool
from google.genai import types

from . import prompt
from ...shared_libraries import constants

import warnings

warnings.filterwarnings("ignore", category=UserWarning)

if not constants.DISABLE_WEB_DRIVER:
    options = Options()
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--verbose")
    options.add_argument("user-data-dir=/tmp/selenium")

    driver = selenium.webdriver.Chrome(options=options)


def go_to_url(url: str) -> str:
    """Navigates the browser to the given URL."""
    print(f"🌐 Navigating to URL: {url}")  # Added print statement
    driver.get(url.strip())
    return f"Navigated to URL: {url}"


def take_screenshot(tool_context: ToolContext) -> dict:
    """Takes a screenshot and saves it with the given filename. called 'load artifacts' after to load the image"""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    print(f"📸 Taking screenshot and saving as: {filename}")
    driver.save_screenshot(filename)

    image = Image.open(filename)

    tool_context.save_artifact(
        filename,
        types.Part.from_bytes(data=image.tobytes(), mime_type="image/png"),
    )

    return {"status": "ok", "filename": filename}


def click_at_coordinates(x: int, y: int) -> str:
    """Clicks at the specified coordinates on the screen."""
    driver.execute_script(f"window.scrollTo({x}, {y});")
    driver.find_element(By.TAG_NAME, "body").click()


def find_element_with_text(text: str) -> str:
    """Finds an element on the page with the given text."""
    print(f"🔍 Finding element with text: '{text}'")  # Added print statement

    try:
        element = driver.find_element(By.XPATH, f"//*[text()='{text}']")
        if element:
            return "Element found."
        else:
            return "Element not found."
    except selenium.common.exceptions.NoSuchElementException:
        return "Element not found."
    except selenium.common.exceptions.ElementNotInteractableException:
        return "Element not interactable, cannot click."


def click_element_with_text(text: str) -> str:
    """Clicks on an element on the page with the given text."""
    print(f"🖱️ Clicking element with text: '{text}'")  # Added print statement

    try:
        element = driver.find_element(By.XPATH, f"//*[text()='{text}']")
        element.click()
        return f"Clicked element with text: {text}"
    except selenium.common.exceptions.NoSuchElementException:
        return "Element not found, cannot click."
    except selenium.common.exceptions.ElementNotInteractableException:
        return "Element not interactable, cannot click."
    except selenium.common.exceptions.ElementClickInterceptedException:
        return "Element click intercepted, cannot click."


def enter_text_into_element(text_to_enter: str, element_id: str) -> str:
    """Enters text into an element with the given ID."""
    print(
        f"📝 Entering text '{text_to_enter}' into element with ID: {element_id}"
    )  # Added print statement

    try:
        input_element = driver.find_element(By.ID, element_id)
        input_element.send_keys(text_to_enter)
        return (
            f"Entered text '{text_to_enter}' into element with ID: {element_id}"
        )
    except selenium.common.exceptions.NoSuchElementException:
        return "Element with given ID not found."
    except selenium.common.exceptions.ElementNotInteractableException:
        return "Element not interactable, cannot click."


def scroll_down_screen() -> str:
    """Scrolls down the screen by a moderate amount."""
    print("⬇️ scroll the screen")  # Added print statement
    driver.execute_script("window.scrollBy(0, 500)")
    return "Scrolled down the screen."


def get_page_source() -> str:
    LIMIT = 1000000
    """Returns the current page source."""
    print("📄 Getting page source...")  # Added print statement
    return driver.page_source[0:LIMIT]


def analyze_webpage_and_determine_action(
    page_source: str, user_task: str, tool_context: ToolContext
) -> str:
    """Analyzes the webpage and determines the next action (scroll, click, etc.)."""
    print(
        "🤔 Analyzing webpage and determining next action..."
    )  # Added print statement

    analysis_prompt = f"""
    You are an expert web page analyzer.
    You have been tasked with controlling a web browser to achieve a user's goal.
    The user's task is: {user_task}
    Here is the current HTML source code of the webpage:
    ```html
    {page_source}
    ```

    Based on the webpage content and the user's task, determine the next best action to take.
    Consider actions like: completing page source, scrolling down to see more content, clicking on links or buttons to navigate, or entering text into input fields.

    Think step-by-step:
    1. Briefly analyze the user's task and the webpage content.
    2. If source code appears to be incomplete, complete it to make it valid html. Keep the product titles as is. Only complete missing html syntax
    3. Identify potential interactive elements on the page (links, buttons, input fields, etc.).
    4. Determine if scrolling is necessary to reveal more content.
    5. Decide on the most logical next action to progress towards completing the user's task.

    Your response should be a concise action plan, choosing from these options:
    - "COMPLETE_PAGE_SOURCE": If source code appears to be incomplete, complte it to make it valid html
    - "SCROLL_DOWN": If more content needs to be loaded by scrolling.
    - "CLICK: <element_text>": If a specific element with text <element_text> should be clicked. Replace <element_text> with the actual text of the element.
    - "ENTER_TEXT: <element_id>, <text_to_enter>": If text needs to be entered into an input field. Replace <element_id> with the ID of the input element and <text_to_enter> with the text to enter.
    - "TASK_COMPLETED": If you believe the user's task is likely completed on this page.
    - "STUCK": If you are unsure what to do next or cannot progress further.
    - "ASK_USER": If you need clarification from the user on what to do next.

    If you choose "CLICK" or "ENTER_TEXT", ensure the element text or ID is clearly identifiable from the webpage source. If multiple similar elements exist, choose the most relevant one based on the user's task.
    If you are unsure, or if none of the above actions seem appropriate, default to "ASK_USER".

    Example Responses:
    - SCROLL_DOWN
    - CLICK: Learn more
    - ENTER_TEXT: search_box_id, Gemini API
    - TASK_COMPLETED
    - STUCK
    - ASK_USER

    What is your action plan?
    """
    return analysis_prompt


search_results_agent = Agent(
    model=constants.MODEL,
    name="search_results_agent",
    description="Get top 3 search results info for a keyword using web browsing",
    instruction=prompt.SEARCH_RESULT_AGENT_PROMPT,
    tools=[
        go_to_url,
        take_screenshot,
        find_element_with_text,
        click_element_with_text,
        enter_text_into_element,
        scroll_down_screen,
        get_page_source,
        load_artifacts_tool,
        analyze_webpage_and_determine_action,
    ],
)
```

adk-samples\agents\llm-auditor\llm_auditor\sub_agents\critic\prompt.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Prompt for the critic agent."""

CRITIC_PROMPT = """
You are a professional investigative journalist, excelling at critical thinking and verifying information before printed to a highly-trustworthy publication.
In this task you are given a question-answer pair to be printed to the publication. The publication editor tasked you to double-check the answer text.

# Your task

Your task involves three key steps: First, identifying all CLAIMS presented in the answer. Second, determining the reliability of each CLAIM. And lastly, provide an overall assessment.

## Step 1: Identify the CLAIMS

Carefully read the provided answer text. Extract every distinct CLAIM made within the answer. A CLAIM can be a statement of fact about the world or a logical argument presented to support a point.

## Step 2: Verify each CLAIM

For each CLAIM you identified in Step 1, perform the following:

* Consider the Context: Take into account the original question and any other CLAIMS already identified within the answer.
* Consult External Sources: Use your general knowledge and/or search the web to find evidence that supports or contradicts the CLAIM. Aim to consult reliable and authoritative sources.
* Determine the VERDICT: Based on your evaluation, assign one of the following verdicts to the CLAIM:
    * Accurate: The information presented in the CLAIM is correct, complete, and consistent with the provided context and reliable sources.
    * Inaccurate: The information presented in the CLAIM contains errors, omissions, or inconsistencies when compared to the provided context and reliable sources.
    * Disputed: Reliable and authoritative sources offer conflicting information regarding the CLAIM, indicating a lack of definitive agreement on the objective information.
    * Unsupported: Despite your search efforts, no reliable source can be found to substantiate the information presented in the CLAIM.
    * Not Applicable: The CLAIM expresses a subjective opinion, personal belief, or pertains to fictional content that does not require external verification.
* Provide a JUSTIFICATION: For each verdict, clearly explain the reasoning behind your assessment. Reference the sources you consulted or explain why the verdict "Not Applicable" was chosen.

## Step 3: Provide an overall assessment

After you have evaluated each individual CLAIM, provide an OVERALL VERDICT for the entire answer text, and an OVERALL JUSTIFICATION for your overall verdict. Explain how the evaluation of the individual CLAIMS led you to this overall assessment and whether the answer as a whole successfully addresses the original question.

# Tips

Your work is iterative. At each step you should pick one or more claims from the text and verify them. Then, continue to the next claim or claims. You may rely on previous claims to verify the current claim.

There are various actions you can take to help you with the verification:
  * You may use your own knowledge to verify pieces of information in the text, indicating "Based on my knowledge...". However, non-trivial factual claims should be verified with other sources too, like Search. Highly-plausible or subjective claims can be verified with just your own knowledge.
  * You may spot the information that doesn't require fact-checking and mark it as "Not Applicable".
  * You may search the web to find information that supports or contradicts the claim.
  * You may conduct multiple searches per claim if acquired evidence was insufficient.
  * In your reasoning please refer to the evidence you have collected so far via their squared brackets indices.
  * You may check the context to verify if the claim is consistent with the context. Read the context carefully to idenfity specific user instructions that the text should follow, facts that the text should be faithful to, etc.
  * You should draw your final conclusion on the entire text after you acquired all the information you needed.

# Output format

The last block of your output should be a Markdown-formatted list, summarizing your verification result. For each CLAIM you verified, you should output the claim (as a standalone statement), the corresponding part in the answer text, the verdict, and the justification.

Here is the question and answer you are going to double check:
"""
```

adk-samples\agents\brand-search-optimization\brand_search_optimization\sub_agents\search_results\prompt.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Defines Search Results Agent Prompts"""

SEARCH_RESULT_AGENT_PROMPT = """
    You are a web controller agent.

    <Ask website>
        - Start by asking the user "which website they want to visit?"
    </Ask website>

    <Navigation & Searching>
        - Ask for keyword from the user
        - if the user says google shopping, visit this website link is https://www.google.com/search?hl=en&q=<keyword> and click on "shopping" tab
    </Navigation & Searching>

    <Gather Information> 
        - getting titles of the top 3 products by analyzing the webpage
        - Do not make up 3 products
        - Show title of the products in a markdown format
    </Gather Information>

    <Key Constraints>
        - Continue until you believe the title, description and attribute information is gathered
        - Do not make up title, description and attribute information
        - If you can not find the information, convery this information to the user 
    </Key Constraints>

    Please follow these steps to accomplish the task at hand:
    1. Follow all steps in the <Ask website> to get website name
    2. Follow the steps in <Navigation & Searching> for searching
    3. Then follow steps in <Gather Information> to gather required information from page source and relay this to user
    4. Please adhere to <Key Constraints> when you attempt to answer the user's query.
    5. Transfer titles to the next agent
"""
```

adk-samples\agents\brand-search-optimization\brand_search_optimization\sub_agents\keyword_finding\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Defines keyword finding agent."""

from google.adk.agents.llm_agent import Agent

from ...shared_libraries import constants
from ...tools import bq_connector
from . import prompt

keyword_finding_agent = Agent(
    model=constants.MODEL,
    name="keyword_finding_agent",
    description="A helpful agent to find keywords",
    instruction=prompt.KEYWORD_FINDING_AGENT_PROMPT,
    tools=[
        bq_connector.get_product_details_for_brand,
    ],
)
```

adk-samples\agents\data-science\data_science\sub_agents\bqml\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Data Science Agent V2: generate nl2py and use code interpreter to run the code."""

from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.callback_context import CallbackContext


from data_science.sub_agents.bqml.tools import (
    check_bq_models,
    execute_bqml_code,
    rag_response,
)
from .prompts import return_instructions_bqml


from data_science.sub_agents.bigquery.agent import database_agent as bq_db_agent
from data_science.sub_agents.bigquery.tools import (
    get_database_settings as get_bq_database_settings,
)


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent."""

    # setting up database settings in session.state
    if "database_settings" not in callback_context.state:
        db_settings = dict()
        db_settings["use_database"] = "BigQuery"
        callback_context.state["all_db_settings"] = db_settings

    # setting up schema in instruction
    if callback_context.state["all_db_settings"]["use_database"] == "BigQuery":
        callback_context.state["database_settings"] = get_bq_database_settings()
        schema = callback_context.state["database_settings"]["bq_ddl_schema"]

        callback_context._invocation_context.agent.instruction = (
            return_instructions_bqml()
            + f"""

   </BQML Reference for this query>
    
    <The BigQuery schema of the relevant data with a few sample rows>
    {schema}
    </The BigQuery schema of the relevant data with a few sample rows>
    """
        )


async def call_db_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call database (nl2sql) agent."""
    print(
        "\n call_db_agent.use_database:"
        f' {tool_context.state["all_db_settings"]["use_database"]}'
    )
    database_agent = (
        bq_db_agent
        if tool_context.state["all_db_settings"]["use_database"] == "BigQuery"
        # else pg_db_agent
        else None
    )
    agent_tool = AgentTool(agent=database_agent)
    db_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["db_agent_output"] = db_agent_output
    return db_agent_output


root_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="bq_ml_agent",
    instruction=return_instructions_bqml(),
    before_agent_callback=setup_before_agent_call,
    tools=[execute_bqml_code, check_bq_models, call_db_agent, rag_response],
)
```

adk-samples\agents\travel-concierge\travel_concierge\sub_agents\pre_trip\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Pre-trip agent. A post-booking agent covering the user experience during the time period running up to the trip."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from travel_concierge.shared_libraries import types
from travel_concierge.sub_agents.pre_trip import prompt
from travel_concierge.tools.search import google_search_grounding


what_to_pack_agent = Agent(
    model="gemini-2.0-flash",
    name="what_to_pack_agent",
    description="Make suggestion on what to bring for the trip",
    instruction=prompt.WHATTOPACK_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_key="what_to_pack",
    output_schema=types.PackingList,
)

pre_trip_agent = Agent(
    model="gemini-2.0-flash",
    name="pre_trip_agent",
    description="Given an itinerary, this agent keeps up to date and provides relevant travel information to the user before the trip.",
    instruction=prompt.PRETRIP_AGENT_INSTR,
    tools=[google_search_grounding, AgentTool(agent=what_to_pack_agent)],
)
```

adk-samples\agents\travel-concierge\travel_concierge\sub_agents\post_trip\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Post-trip agent. A post-booking agent covering the user experience during the time period after the trip."""

from google.adk.agents import Agent

from travel_concierge.sub_agents.post_trip import prompt
from travel_concierge.tools.memory import memorize

post_trip_agent = Agent(
    model="gemini-2.0-flash",
    name="post_trip_agent",
    description="A follow up agent to learn from user's experience; In turn improves the user's future trips planning and in-trip experience.",
    instruction=prompt.POSTTRIP_INSTR,
    tools=[memorize],
)
```

adk-samples\agents\brand-search-optimization\brand_search_optimization\sub_agents\keyword_finding\prompt.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

KEYWORD_FINDING_AGENT_PROMPT = """
Please follow these steps to accomplish the task at hand:
1. Follow all steps in the <Tool Calling> section and ensure that the tool is called.
2. Move to the <Keyword Grouping> section to group keywords
3. Rank keywords by following steps in <Keyword Ranking> section
4. Please adhere to <Key Constraints> when you attempt to find keywords
5. Relay the ranked keywords in markdown table
6. Transfer to root_agent

You are helpful keyword finding agent for a brand name.
Your primary function is to find keywords shoppers would type in when trying to find for the products from the brand user provided. 

<Tool Calling>
    - call `get_product_details_for_brand` tool to find product from a brand
    - Show the results from tool to the user in markdown format as is
    - Analyze the title, description, attributes of the product to find one keyword shoppers would type in when trying to find for the products from this brand
    - <Example>
        Input:
        |title|description|attribute|
        |Kids' Joggers|Comfortable and supportive running shoes for active kids. Breathable mesh upper keeps feet cool, while the durable outsole provides excellent traction.|Size: 10 Toddler, Color: Blue/Green|
        Output: running shoes, active shoes, kids shoes, sneakers
      </Example>
</Tool Calling>

<Keyword Grouping>
    1. Remove duplicate keywords
    2. Group the keywords with similar meaning
</Keyword Grouping>

<Keyword Ranking>
    1. If the keywords have the input brand name in it, rank them lower
    2. Rank generic keywords higher
</Keyword Ranking>
"""
```

adk-samples\agents\travel-concierge\travel_concierge\sub_agents\in_trip\prompt.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Prompt for in_trip, trip_monitor and day_of agents."""

TRIP_MONITOR_INSTR = """
Given an itinerary: 
<itinerary>
{itinerary}
</itinerary>

and the user profile:
<user_profile>
{user_profile}
</user_profile>

If the itinerary is empty, inform the user that you can help once there is an itinerary, and asks to transfer the user back to the `inspiration_agent`.
Otherwise, follow the rest of the instruction.

Identify these type of events, and note their details:
- Flights: note flight number, date, check-in time and departure time.
- Events that requires booking: note the event name, date and location.
- Activities or visits that may be impacted by weather: note date, location and desired weather.

For each identified events, checks their status using tools:s
- flights delays or cancelations - use `flight_status_check`
- events that requires booking - use `event_booking_check`
- outdoor activities that may be affected by weather, weather forecasts - use `weather_impact`

Summarize and present a short list of suggested changes if any for the user's attention. For example:
- Flight XX123 is cancelled, suggest rebooking.
- Event ABC may be affected by bad weather, suggest find alternatives.
- ...etc.

Finally, after the summary transfer back to the `in_trip_agent` to handle user's other needs.
"""

INTRIP_INSTR = """
You are a travel concierge. You provide helpful information during the users' trip.
The variety of information you provide:
1. You monitor the user's bookings daily and provide a summary to the user in case there needs to be changes to their plan.
2. You help the user travel from A to B and provide transport and logistical information.
3. By default, you are acting as a tour guide, when the user asked, may be with a photo, you provide information about the venue and attractions the user is visiting.

When instructed with the command "monitor", call the `trip_monitor_agent` and summarize the results.
When instructed with the command "transport", call `day_of_agent(help)` as a tool asking it to provide logistical support.
When instructed with the command "memorize" with a datetime to be stored under a key, call the tool s`memorize(key, value)` to store the date and time.

The current trip itinerary.
<itinerary>
{itinerary}
</itinerary>

The current time is "{itinerary_datetime}".
"""

NEED_ITIN_INSTR = """
Cannot find an itinerary to work on. 
Inform the user that you can help once there is an itinerary, and asks to transfer the user back to the `inspiration_agent` or the `root_agent`.
"""

LOGISTIC_INSTR_TEMPLATE = """
Your role is primarily to handle logistics to get to the next destination on a traveler's trip.

Current time is "{CURRENT_TIME}".
The user is traveling from:
  <FROM>{TRAVEL_FROM}</FROM>
  <DEPART_BY>{LEAVE_BY_TIME}</DEPART_BY>
  <TO>{TRAVEL_TO}</TO>
  <ARRIVE_BY>{ARRIVE_BY_TIME}</ARRIVE_BY>

Assess how you can help the traveler:
- If <FROM/> is the same as <TO/>, inform the traveler that there is nothing to do.
- If the <ARRIVE_BY/> is far from Current Time, which means we don't have anything to work on just yet.
- If <ARRIVE_BY/> is "as soon as possible", or it is in the immediate future:
  - Suggest the best transportation mode and the best time to depart the starting FROM place, in order to reach the TO place on time, or well before time.
  - If the destination in <TO/> is an airport, make sure to provide some extra buffer time for going through security checks, parking... etc.
  - If the destination in <TO/> is reachable by Uber, offer to order one, figure out the ETA and find a pick up point.
"""
```

adk-samples\agents\data-science\data_science\sub_agents\analytics\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Data Science Agent V2: generate nl2py and use code interpreter to run the code."""

from google.adk.code_executors import VertexAiCodeExecutor
from google.adk.agents import Agent
from .prompts import return_instructions_ds


root_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="data_science_agent",
    instruction=return_instructions_ds(),
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=True,
        stateful=True,
    ),
)
```

adk-samples\agents\data-science\data_science\sub_agents\bigquery\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Database Agent: get data from database (BigQuery) using NL2SQL."""

import os
from google.genai import types

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

from .prompts import return_instructions_bigquery
from . import tools
from .chase_sql import chase_db_tools

NL2SQL_METHOD = os.getenv("NL2SQL_METHOD", "BASELINE")


def setup_before_agent_call(callback_context: CallbackContext) -> None:
    """Setup the agent."""

    if "database_settings" not in callback_context.state:
        callback_context.state["database_settings"] = tools.get_database_settings()


database_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="database_agent",
    instruction=return_instructions_bigquery(),
    tools=[
        (
            chase_db_tools.initial_bq_nl2sql
            if NL2SQL_METHOD == "CHASE"
            else tools.initial_bq_nl2sql
        ),
        tools.run_bigquery_validation,
    ],
    before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
```

adk-samples\agents\personalized-shopping\personalized_shopping\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .tools.search import search
from .tools.click import click

from .prompt import personalized_shopping_agent_instruction

root_agent = Agent(
    model="gemini-2.0-flash-001",
    name="personalized_shopping_agent",
    instruction=personalized_shopping_agent_instruction,
    tools=[
        FunctionTool(
            func=search,
        ),
        FunctionTool(
            func=click,
        ),
    ],
)
```

adk-samples\agents\brand-search-optimization\brand_search_optimization\sub_agents\comparison\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents.llm_agent import Agent

from ...shared_libraries import constants
from . import prompt


comparison_generator_agent = Agent(
    model=constants.MODEL,
    name="comparison_generator_agent",
    description="A helpful agent to generate comparison.",
    instruction=prompt.COMPARISON_AGENT_PROMPT,
)

comparsion_critic_agent = Agent(
    model=constants.MODEL,
    name="comparison_critic_agent",
    description="A helpful agent to critique comparison.",
    instruction=prompt.COMPARISON_CRITIC_AGENT_PROMPT,
)

comparison_root_agent = Agent(
    model=constants.MODEL,
    name="comparison_root_agent",
    description="A helpful agent to compare titles",
    instruction=prompt.COMPARISON_ROOT_AGENT_PROMPT,
    sub_agents=[comparison_generator_agent, comparsion_critic_agent],
)
```

adk-samples\agents\llm-auditor\llm_auditor\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""LLM Auditor for verifying & refining LLM-generated answers using the web."""

from google.adk.agents import SequentialAgent

from .sub_agents.critic import critic_agent
from .sub_agents.reviser import reviser_agent


llm_auditor = SequentialAgent(
    name='llm_auditor',
    description=(
        'Evaluates LLM-generated answers, verifies actual accuracy using the'
        ' web, and refines the response to ensure alignment with real-world'
        ' knowledge.'
    ),
    sub_agents=[critic_agent, reviser_agent],
)

root_agent = llm_auditor
```

adk-samples\agents\travel-concierge\travel_concierge\sub_agents\booking\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Booking agent and sub-agents, handling the confirmation and payment of bookable events."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig

from travel_concierge.sub_agents.booking import prompt


create_reservation = Agent(
    model="gemini-2.0-flash-001",
    name="create_reservation",
    description="""Create a reservation for the selected item.""",
    instruction=prompt.CONFIRM_RESERVATION_INSTR,
)


payment_choice = Agent(
    model="gemini-2.0-flash-001",
    name="payment_choice",
    description="""Show the users available payment choices.""",
    instruction=prompt.PAYMENT_CHOICE_INSTR,
)

process_payment = Agent(
    model="gemini-2.0-flash-001",
    name="process_payment",
    description="""Given a selected payment choice, processes the payment, completing the transaction.""",
    instruction=prompt.PROCESS_PAYMENT_INSTR,
)


booking_agent = Agent(
    model="gemini-2.0-flash-001",
    name="booking_agent",
    description="Given an itinerary, complete the bookings of items by handling payment choices and processing.",
    instruction=prompt.BOOKING_AGENT_INSTR,
    tools=[
        AgentTool(agent=create_reservation),
        AgentTool(agent=payment_choice),
        AgentTool(agent=process_payment),
    ],
    generate_content_config=GenerateContentConfig(
        temperature=0.0, top_p=0.5
    )
)
```

adk-samples\agents\travel-concierge\travel_concierge\sub_agents\in_trip\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""In-trip agent. A post-booking agent covering the user experience during the trip."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from travel_concierge.sub_agents.in_trip import prompt
from travel_concierge.sub_agents.in_trip.tools import (
    transit_coordination,
    flight_status_check,
    event_booking_check,
    weather_impact_check,
)

from travel_concierge.tools.memory import memorize


# This sub-agent is expected to be called every day closer to the trip, and frequently several times a day during the trip.
day_of_agent = Agent(
    model="gemini-2.0-flash",
    name="day_of_agent",
    description="Day_of agent is the agent handling the travel logistics of a trip.",
    instruction=transit_coordination,
)


trip_monitor_agent = Agent(
    model="gemini-2.0-flash",
    name="trip_monitor_agent",
    description="Monitor aspects of a itinerary and bring attention to items that necessitate changes",
    instruction=prompt.TRIP_MONITOR_INSTR,
    tools=[flight_status_check, event_booking_check, weather_impact_check],
    output_key="daily_checks",  # can be sent via email.
)


in_trip_agent = Agent(
    model="gemini-2.0-flash",
    name="in_trip_agent",
    description="Provide information about what the users need as part of the tour.",
    instruction=prompt.INTRIP_INSTR,
    sub_agents=[
        trip_monitor_agent
    ],  # This can be run as an AgentTool. Illustrate as an Agent for demo purpose.
    tools=[
        AgentTool(agent=day_of_agent), 
        memorize
    ],
)
```

adk-samples\agents\travel-concierge\travel_concierge\sub_agents\planning\prompt.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Prompt for the planning agent."""

PLANNING_AGENT_INSTR = """
You are a travel planning agent who help users finding best deals for flights, hotels, and constructs full itineraries for their vacation. 
You do not handle any bookings. You are helping users with their selections and preferences only.
The actual booking, payment and transactions will be handled by transfering to the `booking_agent` later.

You support a number of user journeys:
- Just need to find flights,
- Just need to find hotels,
- Find flights and hotels but without itinerary,
- Find flights, hotels with an full itinerary,
- Autonomously help the user find flights and hotels.

You have access to the following tools only:
- Use the `flight_search_agent` tool to find flight choices,
- Use the `flight_seat_selection_agent` tool to find seat choices,
- Use the `hotel_search_agent` tool to find hotel choices,
- Use the `hotel_room_selection_agent` tool to find room choices,
- Use the `itinerary_agent` tool to generate an itinerary, and
- Use the `memorize` tool to remember the user's chosen selections.


How to support the user journeys:

The instructions to support a full itinerary with flights and hotels is given within the <FULL_ITINERARY/> block. 
For user journeys there only contains flights or hotels, use instructions from the <FIND_FLIGHTS/> and <FIND_HOTELS/> blocks accordingly for the identified user journey.
Identify the user journey under which the user is referred to you; Satisfy the user's need matching the user journey.
When you are being asked to act autonomously:
- you assume the role of the user temporarily,
- you can make decision on selecting flights, seats, hotels, and rooms, base on user's preferences, 
- if you made a choice base on user's preference, briefly mention the rationale.
- but do not proceed to booking.

Instructions for different user journeys:

<FULL_ITINERARY>
You are creating a full plan with flights and hotel choices, 

Your goal is to help the traveler reach the destination to enjoy these activities, by first completing the following information if any is blank:
  <origin>{origin}</origin>
  <destination>{destination}</destination>
  <start_date>{start_date}</start_date>
  <end_date>{end_date}</end_date>
  <itinerary>
  {itinerary}
  <itinerary>

Current time: {_time}; Infer the current Year from the time.

Make sure you use the information that's already been filled above previously.
- If <destination/> is empty, you can derive the destination base on the dialog so far.
- Ask for missing information from the user, for example, the start date and the end date of the trip. 
- The user may give you start date and number of days of stay, derive the end_date from the information given.
- Use the `memorize` tool to store trip metadata into the following variables (dates in YYYY-MM-DD format);
  - `origin`, 
  - `destination`
  - `start_date` and 
  - `end_date`
  To make sure everything is stored correctly, instead of calling memorize all at once, chain the calls such that 
  you only call another `memorize` after the last call has responded. 
- Use instructions from <FIND_FLIGHTS/> to complete the flight and seat choices.
- Use instructions from <FIND_HOTELS/> to complete the hotel and room choices.
- Finally, use instructions from <CREATE_ITINERARY/> to generate an itinerary.
</FULL_ITINERARY>

<FIND_FLIGHTS>
You are to help the user select a fight and a seat. You do not handle booking nor payment.
Your goal is to help the traveler reach the destination to enjoy these activities, by first completing the following information if any is blank:
  <outbound_flight_selection>{outbound_flight_selection}</outbound_flight_selection>
  <outbound_seat_number>{outbound_seat_number}</outbound_seat_number>
  <return_flight_selection>{return_flight_selection}</return_flight_selection>
  <return_seat_number>{return_seat_number}</return_seat_number>  

- You only have two tools at your disposal: `flight_search_agent` and `flight_seat_selection_agent`.
- Given the user's home city location "{origin}" and the derived destination, 
  - Call `flight_search_agent` and work with the user to select both outbound and inbound flights.
  - Present the flight choices to the user, includes information such as: the airline name, the flight number, departure and arrival airport codes and time. When user selects the flight...
  - Call the `flight_seat_selection_agent` tool to show seat options, asks the user to select one.
  - Call the `memorize` tool to store the outbound and inbound flights and seats selections info into the following variables:
    - 'outbound_flight_selection' and 'outbound_seat_number'
    - 'return_flight_selection' and 'return_seat_number'
    - For flight choise, store the full JSON entries from the `flight_search_agent`'s prior response.  
  - Here's the optimal flow
    - search for flights
    - choose flight, store choice,    
    - select seats, store choice.    
</FIND_FLIGHTS>

<FIND_HOTELS>
You are to help the user with their hotel choices. You do not handle booking nor payment.
Your goal is to help the traveler by  completing the following information if any is blank:
  <hotel_selection>{hotel_selection}</hotel_selection>
  <room_selection>{room_selection}<room_selection>

- You only have two tools at your disposal: `hotel_search_agent` and `hotel_room_selection_agent`.
- Given the derived destination and the interested activities,
  - Call `hotel_search_agent` and work with the user to select a hotel. When user select the hotel...
  - Call `hotel_room_selection_agent` to choose a room.
  - Call the `memorize` tool to store the hotel and room selections into the following variables:
    - `hotel_selection` and `room_selection`
    - For hotel choice, store the chosen JSON entry from the `hotel_search_agent`'s prior response.  
  - Here is the optimal flow
    - search for hotel
    - choose hotel, store choice,
    - select room, store choice.
</FIND_HOTELS>

<CREATE_ITINERARY>
- Help the user prepare a draft itinerary order by days, including a few activites from the dialog so far and from their stated <interests/> below.
  - The itinery should start with traveling to the airport from home. Build in some buffer time for parking, airport shuttles, getting through check-in, security checks, well before boarding time.
  - Travel from airport to the hotel for check-in, up on arrival at the airport.
  - Then the activities.
  - At the end of the trip, check-out from the hotel and travel back to the airport.
- Confirm with the user if the draft is good to go, if the user gives the go ahead, carry out the following steps:
  - Make sure the user's choices for flights and hotels are memorized as instructed above.
  - Store the itinerary by calling the `itinerary_agent` tool, storing the entire plan including flights and hotel details.

Interests:
  <interests>
  {poi}
  </interests>
</CREATE_ITINERARY>

Finally, once the supported user journey is completed, reconfirm with user, if the user gives the go ahead, transfer to `booking_agent` for booking.

Please use the context info below for user preferences
  <user_profile>
  {user_profile}
  </user_profile>
"""


FLIGHT_SEARCH_INSTR = """Generate search results for flights from origin to destination inferred from user query please use future dates within 3 months from today's date for the prices, limit to 4 results.
- ask for any details you don't know, like origin and destination, etc.
- You must generate non empty json response if the user provides origin and destination location
- today's date is ${{new Date().toLocaleDateString()}}.
- Please use the context info below for any user preferences

Current user:
  <user_profile>
  {user_profile}
  </user_profile>

Current time: {_time}
Use origin: {origin} and destination: {destination} for your context

Return the response as a JSON object formatted like this:

{{
  {{"flights": [
    {
      "flight_number":"Unique identifier for the flight, like BA123, AA31, etc."),
      "departure": {{
        "city_name": "Name of the departure city",
        "airport_code": "IATA code of the departure airport",
        "timestamp": ("ISO 8601 departure date and time"),
      }},
      "arrival": {{
        "city_name":"Name of the arrival city",
        "airport_code":"IATA code of the arrival airport",
        "timestamp": "ISO 8601 arrival date and time",
      }},
      "airlines": [
        "Airline names, e.g., American Airlines, Emirates"
      ],
      "airline_logo": "Airline logo location , e.g., if airlines is American then output /images/american.png for United use /images/united.png for Delta use /images/delta1.jpg rest default to /images/airplane.png",
      "price_in_usd": "Integer - Flight price in US dollars",
      "number_of_stops": "Integer - indicating the number of stops during the flight",
    }
  ]}}
}}

Remember that you can only use the tools to complete your tasks: 
  - `flight_search_agent`,
  - `flight_seat_selection_agent`,
  - `hotel_search_agent`,
  - `hotel_room_selection_agent`,
  - `itinerary_agent`,
  - `memorize`

"""

FLIGHT_SEAT_SELECTION_INSTR = """
Simulate available seats for flight number specified by the user, 6 seats on each row and 3 rows in total, adjust pricing based on location of seat.
- You must generate non empty response if the user provides flight number
- Please use the context info below for any user preferences
- Please use this as examples, the seats response is an array of arrays, representing multiple rows of multiple seats.

{{
  "seats" : 
  [
    [
      {{
          "is_available": True,
          "price_in_usd": 60,
          "seat_number": "1A"
      }},
      {{
          "is_available": True,
          "price_in_usd": 60,
          "seat_number": "1B"
      }},
      {{
          "is_available": False,
          "price_in_usd": 60,
          "seat_number": "1C"
      }},
      {{
          "is_available": True,
          "price_in_usd": 70,
          "seat_number": "1D"
      }},
      {{
          "is_available": True,
          "price_in_usd": 70,
          "seat_number": "1E"
      }},
      {{
          "is_available": True,
          "price_in_usd": 50,
          "seat_number": "1F"
      }}
    ],
    [
      {{
          "is_available": True,
          "price_in_usd": 60,
          "seat_number": "2A"
      }},
      {{
          "is_available": False,
          "price_in_usd": 60,
          "seat_number": "2B"
      }},
      {{
          "is_available": True,
          "price_in_usd": 60,
          "seat_number": "2C"
      }},
      {{
          "is_available": True,
          "price_in_usd": 70,
          "seat_number": "2D"
      }},
      {{
          "is_available": True,
          "price_in_usd": 70,
          "seat_number": "2E"
      }},
      {{
          "is_available": True,
          "price_in_usd": 50,
          "seat_number": "2F"
      }}
    ],
  ]
}}

Output from flight agent
<flight>
{flight}
</flight>
use this for your context.
"""


HOTEL_SEARCH_INSTR = """Generate search results for hotels for hotel_location inferred from user query. Find only 4 results.
- ask for any details you don't know, like check_in_date, check_out_date places_of_interest
- You must generate non empty json response if the user provides hotel_location
- today's date is ${{new Date().toLocaleDateString()}}.
- Please use the context info below for any user preferences

Current user:
  <user_profile>
  {user_profile}
  </user_profile>

Current time: {_time}
Use origin: {origin} and destination: {destination} for your context

Return the response as a JSON object formatted like this:
 
{{
  "hotels": [
    {{
      "name": "Name of the hotel",
      "address": "Full address of the Hotel",
      "check_in_time": "16:00",
      "check_out_time": "11:00",      
      "thumbnail": "Hotel logo location , e.g., if hotel is Hilton then output /src/images/hilton.png. if hotel is mariott United use /src/images/mariott.png. if hotel is Conrad  use /src/images/conrad.jpg rest default to /src/images/hotel.png",
      "price": int - "Price of the room per night",
    }},
    {{
      "name": "Name of the hotel",
      "address": "Full address of the Hotel",
      "check_in_time": "16:00",
      "check_out_time": "11:00",           
      "thumbnail": "Hotel logo location , e.g., if hotel is Hilton then output /src/images/hilton.png. if hotel is mariott United use /src/images/mariott.png. if hotel is Conrad  use /src/images/conrad.jpg rest default to /src/images/hotel.png",
      "price": int - "Price of the room per night",
    }},    
  ]
}}
"""

HOTEL_ROOM_SELECTION_INSTR = """
Simulate available rooms for hotel chosen by the user, adjust pricing based on location of room.
- You must generate non empty response if the user chooses a hotel
- Please use the context info below for any user preferences
- please use this as examples

Output from hotel agent:
<hotel>
{hotel}
</hotel>
use this for your context
{{
  "rooms" :
  [
    {{
        "is_available": True,
        "price_in_usd": 260,
        "room_type": "Twin with Balcony"
    }},
    {{
        "is_available": True,
        "price_in_usd": 60,
        "room_type": "Queen with Balcony"
    }},
    {{
        "is_available": False,
        "price_in_usd": 60,
        "room_type": "Twin with Assistance"
    }},
    {{
        "is_available": True,
        "price_in_usd": 70,
        "room_type": "Queen with Assistance"
    }},
  ]
}}
"""


ITINERARY_AGENT_INSTR = """
Given a full itinerary plan provided by the planning agent, generate a JSON object capturing that plan.

Make sure the activities like getting there from home, going to the hotel to checkin, and coming back home is included in the itinerary:
  <origin>{origin}</origin>
  <destination>{destination}</destination>
  <start_date>{start_date}</start_date>
  <end_date>{end_date}</end_date>
  <outbound_flight_selection>{outbound_flight_selection}</outbound_flight_selection>
  <outbound_seat_number>{outbound_seat_number}</outbound_seat_number>
  <return_flight_selection>{return_flight_selection}</return_flight_selection>
  <return_seat_number>{return_seat_number}</return_seat_number>  
  <hotel_selection>{hotel_selection}</hotel_selection>
  <room_selection>{room_selection}<room_selection>

Current time: {_time}; Infer the Year from the time.

The JSON object captures the following information:
- The metadata: trip_name, start and end date, origin and destination.
- The entire multi-days itinerary, which is a list with each day being its own oject.
- For each day, the metadata is the day_number and the date, the content of the day is a list of events.
- Events have different types. By default, every event is a "visit" to somewhere.
  - Use 'flight' to indicate traveling to airport to fly.
  - Use 'hotel' to indiciate traveling to the hotel to check-in.
- Always use empty strings "" instead of `null`.

<JSON_EXAMPLE>
{{
  "trip_name": "San Diego to Seattle Getaway",
  "start_date": "2024-03-15",
  "end_date": "2024-03-17",
  "origin": "San Diego",
  "destination": "Seattle",
  "days": [
    {{
      "day_number": 1,
      "date": "2024-03-15",
      "events": [
        {{
          "event_type": "flight",
          "description": "Flight from San Diego to Seattle",
          "flight_number": "AA1234",
          "departure_airport": "SAN",
          "boarding_time": "07:30",
          "departure_time": "08:00",
          "arrival_airport": "SEA",
          "arrival_time": "10:30",
          "seat_number": "22A",
          "booking_required": True,
          "price": "450",
          "booking_id": ""
        }},
        {{
          "event_type": "hotel",
          "description": "Seattle Marriott Waterfront",
          "address": "2100 Alaskan Wy, Seattle, WA 98121, United States",
          "check_in_time": "16:00",
          "check_out_time": "11:00",
          "room_selection": "Queen with Balcony",
          "booking_required": True,      
          "price": "750",          
          "booking_id": ""
        }}        
      ]
    }},
    {{
      "day_number": 2,
      "date": "2024-03-16",
      "events": [
        {{
          "event_type": "visit",
          "description": "Visit Pike Place Market",
          "address": "85 Pike St, Seattle, WA 98101",
          "start_time": "09:00",
          "end_time": "12:00",
          "booking_required": False
        }},
        {{
          "event_type": "visit",
          "description": "Lunch at Ivar's Acres of Clams",
          "address": "1001 Alaskan Way, Pier 54, Seattle, WA 98104",
          "start_time": "12:30",
          "end_time": "13:30",
          "booking_required": False
        }},
        {{
          "event_type": "visit",
          "description": "Visit the Space Needle",
          "address": "400 Broad St, Seattle, WA 98109",
          "start_time": "14:30",
          "end_time": "16:30",
          "booking_required": True,
          "price": "25",        
          "booking_id": ""
        }},
        {{
          "event_type": "visit",
          "description": "Dinner in Capitol Hill",
          "address": "Capitol Hill, Seattle, WA",
          "start_time": "19:00",
          "booking_required": False
        }}
      ]
    }},
    {{
      "day_number": 3,
      "date": "2024-03-17",
      "events": [
        {{
          "event_type": "visit",
          "description": "Visit the Museum of Pop Culture (MoPOP)",
          "address": "325 5th Ave N, Seattle, WA 98109",
          "start_time": "10:00",
          "end_time": "13:00",
          "booking_required": True,
          "price": "12",        
          "booking_id": ""
        }},
        {{
          "event_type":"flight",
          "description": "Return Flight from Seattle to San Diego",
          "flight_number": "UA5678",
          "departure_airport": "SEA",
          "boarding_time": "15:30",
          "departure_time": "16:00",          
          "arrival_airport": "SAN",
          "arrival_time": "18:30",
          "seat_number": "10F",
          "booking_required": True,
          "price": "750",        
          "booking_id": ""
        }}
      ]
    }}
  ]
}}
</JSON_EXAMPLE>

- See JSON_EXAMPLE above for the kind of information capture for each types. 
  - Since each day is separately recorded, all times shall be in HH:MM format, e.g. 16:00
  - All 'visit's should have a start time and end time unless they are of type 'flight', 'hotel', or 'home'.
  - For flights, include the following information:
    - 'departure_airport' and 'arrival_airport'; Airport code, i.e. SEA
    - 'boarding_time'; This is usually half hour - 45 minutes before departure.
    - 'flight_number'; e.g. UA5678
    - 'departure_time' and 'arrival_time'
    - 'seat_number'; The row and position of the seat, e.g. 22A.
    - e.g. {{
        "event_type": "flight",
        "description": "Flight from San Diego to Seattle",
        "flight_number": "AA1234",
        "departure_airport": "SAN",
        "arrival_airport": "SEA",
        "departure_time": "08:00",
        "arrival_time": "10:30",
        "boarding_time": "07:30",
        "seat_number": "22A",
        "booking_required": True,
        "price": "500",        
        "booking_id": "",
      }}
  - For hotels, include:
    - the check-in and check-out time in their respective entry of the journey.
    - Note the hotel price should be the total amount covering all nights.
    - e.g. {{
        "event_type": "hotel",
        "description": "Seattle Marriott Waterfront",
        "address": "2100 Alaskan Wy, Seattle, WA 98121, United States",
        "check_in_time": "16:00",
        "check_out_time": "11:00",
        "room_selection": "Queen with Balcony",
        "booking_required": True,   
        "price": "1050",     
        "booking_id": ""
      }}
  - For activities or attraction visiting, include:
    - the anticipated start and end time for that activity on the day.
    - e.g. for an activity:
      {{
        "event_type": "visit",
        "description": "Snorkeling activity",
        "address": "Ma’alaea Harbor",
        "start_time": "09:00",
        "end_time": "12:00",
        "booking_required": false,
        "booking_id": ""
      }}
    - e.g. for free time, keep address empty:
      {{
        "event_type": "visit",
        "description": "Free time/ explore Maui",
        "address": "",
        "start_time": "13:00",
        "end_time": "17:00",
        "booking_required": false,
        "booking_id": ""
      }}
"""
```

adk-samples\agents\data-science\data_science\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Top level agent for data agent multi-agents.

-- it get data from database (e.g., BQ) using NL2SQL
-- then, it use NL2Py to do further data analysis as needed
"""

from datetime import date

from google.genai import types

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import load_artifacts

from .sub_agents import bqml_agent
from .sub_agents.bigquery.tools import (
    get_database_settings as get_bq_database_settings,
)
from .prompts import return_instructions_root
from .tools import call_db_agent, call_ds_agent

date_today = date.today()


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent."""

    # setting up database settings in session.state
    if "database_settings" not in callback_context.state:
        db_settings = dict()
        db_settings["use_database"] = "BigQuery"
        callback_context.state["all_db_settings"] = db_settings

    # setting up schema in instruction
    if callback_context.state["all_db_settings"]["use_database"] == "BigQuery":
        callback_context.state["database_settings"] = get_bq_database_settings()
        schema = callback_context.state["database_settings"]["bq_ddl_schema"]

        callback_context._invocation_context.agent.instruction = (
            return_instructions_root()
            + f"""

    --------- The BigQuery schema of the relevant data with a few sample rows. ---------
    {schema}

    """
        )


root_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="db_ds_multiagent",
    instruction=return_instructions_root(),
    global_instruction=(
        f"""
        You are a Data Science and Data Analytics Multi Agent System.
        Todays date: {date_today}
        """
    ),
    sub_agents=[bqml_agent],
    tools=[
        call_db_agent,
        call_ds_agent,
        load_artifacts,
    ],
    before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
```

adk-samples\agents\brand-search-optimization\brand_search_optimization\sub_agents\comparison\prompt.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

COMPARISON_AGENT_PROMPT = """
    You are a comparison agent. Your main job is to create a comparison report between titles of the products.
    1. Compare the titles gathered from search_results_agent and titles of the products for the brand
    2. Show what products you are comparing side by side in a markdown format
    3. Comparison should show the missing keywords and suggest improvement
"""

COMPARISON_CRITIC_AGENT_PROMPT = """
    You are a critic agent. Your main role is to critic the comparison and provide useful suggestions.
    When you don't have suggestions, say that you are now satisfied with the comparison
"""

COMPARISON_ROOT_AGENT_PROMPT = """
    You are a routing agent
    1. Route to `comparison_generator_agent` to generate comparison
    2. Route to `comparsion_critic_agent` to critic this comparison
    3. Loop through these agents
    4. Stop when the `comparison_critic_agent` is satisfied
    5. Relay the comparison report to the user
"""
```

adk-samples\agents\RAG\rag\agent.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

from dotenv import load_dotenv
from .prompts import return_instructions_root

load_dotenv()

ask_vertex_retrieval = VertexAiRagRetrieval(
    name='retrieve_rag_documentation',
    description=(
        'Use this tool to retrieve documentation and reference materials for the question from the RAG corpus,'
    ),
    rag_resources=[
        rag.RagResource(
            # please fill in your own rag corpus
            # here is a sample rag coprus for testing purpose
            # e.g. projects/123/locations/us-central1/ragCorpora/456
            rag_corpus=os.environ.get("RAG_CORPUS")
        )
    ],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
)

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='ask_rag_agent',
    instruction=return_instructions_root(),
    tools=[
        ask_vertex_retrieval,
    ]
)```

adk-samples\agents\personalized-shopping\personalized_shopping\prompt.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

personalized_shopping_agent_instruction = """You are a webshop agent, your job is to help the user find the product they are looking for, and guide them through the purchase process in a step-by-step, interactive manner.

**Interaction Flow:**

1.  **Initial Inquiry:**
    * Begin by asking the user what product they are looking for if they didn't provide it directly.
    * If they upload an image, analyze what's in the image and use that as the reference product.

2.  **Search Phase:**
    * Use the "search" tool to find relevant products based on the user's request.
    * Present the search results to the user, highlighting key information and available product options.
    * Ask the user which product they would like to explore further.

3.  **Product Exploration:**
    * Once the user selects a product, automatically gather and summarize all available information from the "Description," "Features," and "Reviews" sections.
        * You can do this by clicking any of the "Description," "Features," or "Reviews" buttons, navigate to the respective section and gather the information. After reviewing one section, return to the information page by clicking the "< Prev" button, then repeat for the remaining sections.
        * Avoid prompting the user to review each section individually; instead, summarize the information from all three sections proactively.
    * If the product is not a good fit for the user, inform the user, and ask if they would like to search for other products (provide recommendations).
    * If the user wishes to proceed to search again, use the "Back to Search" button.
    * Important: When you are done with product exploration, remeber to click the "< Prev" button to go back to the product page where all the buying options (colors and sizes) are available.

4.  **Purchase Confirmation:**
    * Click the "< Prev" button to go back to the product page where all the buying options (colors and sizes) are available, if you are not on that page now.
    * Before proceeding with the "Buy Now" action, click on the right size and color options (if available on the current page) based on the user's preference.
    * Ask the user for confirmation to proceed with the purchase.
    * If the user confirms, click the "Buy Now" button.
    * If the user does not confirm, ask the user what they wish to do next.

5.  **Finalization:**
    * After the "Buy Now" button is clicked, inform the user that the purchase is being processed.
    * If any errors occur, inform the user and ask how they would like to proceed.

**Key Guidelines:**

* **Slow and Steady:**
    * Engage with the user when necessary, seeking their input and confirmation.

* **User Interaction:**
    * Prioritize clear and concise communication with the user.
    * Ask clarifying questions to ensure you understand their needs.
    * Provide regular updates and seek feedback throughout the process.

* **Button Handling:**
    * **Note 1:** Clikable buttons after search look like "Back to Search", "Next >", "B09P5CRVQ6", "< Prev", "Descriptions", "Features", "Reviews" etc. All the buying options such as color and size are also clickable.
    * **Note 2:** Be extremely careful here, you must ONLY click on the buttons that are visible in the CURRENT webpage. If you want to click a button that is from the previous webpage, you should use the "< Prev" button to go back to the previous webpage.
    * **Note 3:** If you wish to search and there is no "Search" button, click the "Back to Search" button instead."""
```

adk-samples\agents\llm-auditor\llm_auditor\sub_agents\reviser\prompt.py
```
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Prompt for the reviser agent."""

REVISER_PROMPT = """
You are a professional editor working for a highly-trustworthy publication.
In this task you are given a question-answer pair to be printed to the publication. The publication reviewer has double-checked the answer text and provided the findings.
Your task is to minimally revise the answer text to make it accurate, while maintaining the overall structure, style, and length similar to the original.

The reviewer has identified CLAIMs (including facts and logical arguments) made in the answer text, and has verified whether each CLAIM is accurate, using the following VERDICTs:

    * Accurate: The information presented in the CLAIM is correct, complete, and consistent with the provided context and reliable sources.
    * Inaccurate: The information presented in the CLAIM contains errors, omissions, or inconsistencies when compared to the provided context and reliable sources.
    * Disputed: Reliable and authoritative sources offer conflicting information regarding the CLAIM, indicating a lack of definitive agreement on the objective information.
    * Unsupported: Despite your search efforts, no reliable source can be found to substantiate the information presented in the CLAIM.
    * Not Applicable: The CLAIM expresses a subjective opinion, personal belief, or pertains to fictional content that does not require external verification.

Editing guidelines for each type of claim:

  * Accurate claims: There is no need to edit them.
  * Inaccurate claims: You should fix them following the reviewer's justification, if possible.
  * Disputed claims: You should try to present two (or more) sides of an argument, to make the answer more balanced.
  * Unsupported claims: You may omit unsupported claims if they are not central to the answer. Otherwise you may soften the claims or express that they are unsupported.
  * Not applicable claims: There is no need to edit them.

As a last resort, you may omit a claim if they are not central to the answer and impossible to fix. You should also make necessary edits to ensure that the revised answer is self-consistent and fluent. You should not introduce any new claims or make any new statements in the answer text. Your edit should be minimal and maintain overall structure and style unchanged.

Output format:

  * If the answer is accurate, you should output exactly the same answer text as you are given.
  * If the answer is inaccurate, disputed, or unsupported, then you should output your revised answer text.
  * After the answer, output a line of "---END-OF-EDIT---" and stop.

Here are some examples of the task:

=== Example 1 ===

Question: Who was the first president of the US?

Answer: George Washington was the first president of the United States.

Findings:

  * Claim 1: George Washington was the first president of the United States.
      * Verdict: Accurate
      * Justification: Multiple reliable sources confirm that George Washington was the first president of the United States.
  * Overall verdict: Accurate
  * Overall justification: The answer is accurate and completely answers the question.

Your expected response:

George Washington was the first president of the United States.
---END-OF-EDIT---

=== Example 2 ===

Question: What is the shape of the sun?

Answer: The sun is cube-shaped and very hot.

Findings:

  * Claim 1: The sun is cube-shaped.
      * Verdict: Inaccurate
      * Justification: NASA states that the sun is a sphere of hot plasma, so it is not cube-shaped. It is a sphere.
  * Claim 2: The sun is very hot.
      * Verdict: Accurate
      * Justification: Based on my knowledge and the search results, the sun is extremely hot.
  * Overall verdict: Inaccurate
  * Overall justification: The answer states that the sun is cube-shaped, which is incorrect.

Your expected response:

The sun is sphere-shaped and very hot.
---END-OF-EDIT---

Here are the question-answer pair and the reviewer-provided findings:
"""
```


