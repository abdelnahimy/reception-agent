# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

import os
try:
    _, project_id = google.auth.default()
except Exception:
    project_id = None

if project_id:
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
else:
    # Set a fallback project ID to avoid TypeError
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "local-reception-project")

os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
# If GEMINI_API_KEY or GOOGLE_API_KEY is present in env, default to AI Studio (not Vertex)
if "GEMINI_API_KEY" in os.environ or "GOOGLE_API_KEY" in os.environ:
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")
else:
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")



from app.database import init_db
from app.tools import list_bookings, check_availability, create_booking, cancel_booking, answer_faq

# Initialize SQLite database and tables
init_db()

def get_current_time() -> str:
    """Get the current date and time. Use this when the guest asks what day/time it is or if they need to check the current date/time to make a booking.

    Returns:
        A string containing the current date and time.
    """
    now = datetime.datetime.now()
    return f"The current date and time is {now.strftime('%Y-%m-%d %H:%M:%S')}"

root_agent = Agent(
    name="reception_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are the company's Reception Assistant. Your job is to help visitors and employees automate daily reception tasks.
You can help them with:
1. Checking room or table availability.
2. Creating bookings/reservations for rooms or lunch tables.
3. Listing existing bookings.
4. Cancelling bookings when requested.
5. Answering frequently asked questions (FAQs) about Wi-Fi, reception hours, parking, office address, and contact details.

Rules:
- You must always query/use the tools provided.
- Before confirming a booking, verify availability first. If available, confirm the guest's name, booking date, time, duration, and resource name, and ask the user for confirmation before calling `create_booking`.
- Do not allow booking dates in the past or times outside of business hours (08:00 to 18:00).
- If a resource is unavailable, suggest alternative resources or suggest checking availability for other times.
- Always be polite, welcoming, and professional.
""",
    tools=[list_bookings, check_availability, create_booking, cancel_booking, answer_faq, get_current_time],
)

app = App(
    root_agent=root_agent,
    name="app",
)

