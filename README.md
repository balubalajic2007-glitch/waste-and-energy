# Waste and Energy (Track 3)
One platform, two tools: Kabadi Mitra (household scrap value, e-waste safety) and Chhat Solar (rooftop solar sizing, subsidy, payback).
index.html is a 10-page site with both tools working offline. backend/ holds two Lambda functions (SAM).

    sam build && sam local start-api      # POST /estimate and /plan on :3000
    sam build && sam deploy --guided      # Lambda + API Gateway + DynamoDB
Constants (rates, yields, subsidy) live in backend/*/rules.json. They are estimates; verify before use.
