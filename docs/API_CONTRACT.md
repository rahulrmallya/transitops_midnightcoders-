# TransitOps API Contract

This document is the single source of truth between the frontend and backend.

## Base URL

```text
/api/v1
```

## Standard Response Format

Success:

```json
{
  "success": true,
  "message": "",
  "data": {}
}
```

Failure:

```json
{
  "success": false,
  "message": "",
  "errors": {}
}
```

All endpoints must use this response format.

## Authentication

### POST /auth/login

Purpose: Authenticate a user and return an access token.

Request Body:

```json
{
  "placeholder": "login payload"
}
```

Response Body:

```json
{
  "success": true,
  "message": "Login successful",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `400 Bad Request`, `401 Unauthorized`, `422 Unprocessable Entity`, `500 Internal Server Error`

### POST /auth/register

Purpose: Register a new user account.

Request Body:

```json
{
  "placeholder": "registration payload"
}
```

Response Body:

```json
{
  "success": true,
  "message": "Registration successful",
  "data": {}
}
```

HTTP Status Codes: `201 Created`, `400 Bad Request`, `409 Conflict`, `422 Unprocessable Entity`, `500 Internal Server Error`

### GET /auth/me

Purpose: Return the authenticated user's profile.

Request Body:

```json
{}
```

Response Body:

```json
{
  "success": true,
  "message": "User profile retrieved",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `401 Unauthorized`, `404 Not Found`, `500 Internal Server Error`

## Vehicles

### GET /vehicles

Purpose: List vehicles.

Request Body:

```json
{}
```

Response Body:

```json
{
  "success": true,
  "message": "Vehicles retrieved",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `401 Unauthorized`, `500 Internal Server Error`

### GET /vehicles/{id}

Purpose: Retrieve a vehicle by ID.

Request Body:

```json
{}
```

Response Body:

```json
{
  "success": true,
  "message": "Vehicle retrieved",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `401 Unauthorized`, `404 Not Found`, `500 Internal Server Error`

### POST /vehicles

Purpose: Create a vehicle.

Request Body:

```json
{
  "placeholder": "vehicle payload"
}
```

Response Body:

```json
{
  "success": true,
  "message": "Vehicle created",
  "data": {}
}
```

HTTP Status Codes: `201 Created`, `400 Bad Request`, `401 Unauthorized`, `409 Conflict`, `422 Unprocessable Entity`, `500 Internal Server Error`

### PUT /vehicles/{id}

Purpose: Update a vehicle.

Request Body:

```json
{
  "placeholder": "vehicle update payload"
}
```

Response Body:

```json
{
  "success": true,
  "message": "Vehicle updated",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity`, `500 Internal Server Error`

### DELETE /vehicles/{id}

Purpose: Delete a vehicle.

Request Body:

```json
{}
```

Response Body:

```json
{
  "success": true,
  "message": "Vehicle deleted",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `401 Unauthorized`, `404 Not Found`, `409 Conflict`, `500 Internal Server Error`

## Drivers

### GET /drivers

Purpose: List drivers.

Request Body:

```json
{}
```

Response Body:

```json
{
  "success": true,
  "message": "Drivers retrieved",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `401 Unauthorized`, `500 Internal Server Error`

### GET /drivers/{id}

Purpose: Retrieve a driver by ID.

Request Body:

```json
{}
```

Response Body:

```json
{
  "success": true,
  "message": "Driver retrieved",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `401 Unauthorized`, `404 Not Found`, `500 Internal Server Error`

### POST /drivers

Purpose: Create a driver.

Request Body:

```json
{
  "placeholder": "driver payload"
}
```

Response Body:

```json
{
  "success": true,
  "message": "Driver created",
  "data": {}
}
```

HTTP Status Codes: `201 Created`, `400 Bad Request`, `401 Unauthorized`, `409 Conflict`, `422 Unprocessable Entity`, `500 Internal Server Error`

### PUT /drivers/{id}

Purpose: Update a driver.

Request Body:

```json
{
  "placeholder": "driver update payload"
}
```

Response Body:

```json
{
  "success": true,
  "message": "Driver updated",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity`, `500 Internal Server Error`

### DELETE /drivers/{id}

Purpose: Delete a driver.

Request Body:

```json
{}
```

Response Body:

```json
{
  "success": true,
  "message": "Driver deleted",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `401 Unauthorized`, `404 Not Found`, `409 Conflict`, `500 Internal Server Error`

## Trips

### GET /trips

Purpose: List trips.

Request Body:

```json
{}
```

Response Body:

```json
{
  "success": true,
  "message": "Trips retrieved",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `401 Unauthorized`, `500 Internal Server Error`

### GET /trips/{id}

Purpose: Retrieve a trip by ID.

Request Body:

```json
{}
```

Response Body:

```json
{
  "success": true,
  "message": "Trip retrieved",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `401 Unauthorized`, `404 Not Found`, `500 Internal Server Error`

### POST /trips

Purpose: Create a trip.

Request Body:

```json
{
  "placeholder": "trip payload"
}
```

Response Body:

```json
{
  "success": true,
  "message": "Trip created",
  "data": {}
}
```

HTTP Status Codes: `201 Created`, `400 Bad Request`, `401 Unauthorized`, `409 Conflict`, `422 Unprocessable Entity`, `500 Internal Server Error`

### PATCH /trips/{id}/dispatch

Purpose: Mark a trip as dispatched.

Request Body:

```json
{
  "placeholder": "dispatch payload"
}
```

Response Body:

```json
{
  "success": true,
  "message": "Trip dispatched",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity`, `500 Internal Server Error`

### PATCH /trips/{id}/complete

Purpose: Mark a trip as completed.

Request Body:

```json
{
  "placeholder": "completion payload"
}
```

Response Body:

```json
{
  "success": true,
  "message": "Trip completed",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity`, `500 Internal Server Error`

### PATCH /trips/{id}/cancel

Purpose: Mark a trip as cancelled.

Request Body:

```json
{
  "placeholder": "cancellation payload"
}
```

Response Body:

```json
{
  "success": true,
  "message": "Trip cancelled",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity`, `500 Internal Server Error`

## Maintenance

### GET /maintenance

Purpose: List maintenance records.

Request Body:

```json
{}
```

Response Body:

```json
{
  "success": true,
  "message": "Maintenance records retrieved",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `401 Unauthorized`, `500 Internal Server Error`

### POST /maintenance

Purpose: Create a maintenance record.

Request Body:

```json
{
  "placeholder": "maintenance payload"
}
```

Response Body:

```json
{
  "success": true,
  "message": "Maintenance record created",
  "data": {}
}
```

HTTP Status Codes: `201 Created`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `422 Unprocessable Entity`, `500 Internal Server Error`

### PATCH /maintenance/{id}/close

Purpose: Close a maintenance record.

Request Body:

```json
{
  "placeholder": "maintenance close payload"
}
```

Response Body:

```json
{
  "success": true,
  "message": "Maintenance record closed",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity`, `500 Internal Server Error`

## Fuel

### GET /fuel

Purpose: List fuel logs.

Request Body:

```json
{}
```

Response Body:

```json
{
  "success": true,
  "message": "Fuel logs retrieved",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `401 Unauthorized`, `500 Internal Server Error`

### POST /fuel

Purpose: Create a fuel log.

Request Body:

```json
{
  "placeholder": "fuel log payload"
}
```

Response Body:

```json
{
  "success": true,
  "message": "Fuel log created",
  "data": {}
}
```

HTTP Status Codes: `201 Created`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `422 Unprocessable Entity`, `500 Internal Server Error`

## Expenses

### GET /expenses

Purpose: List expenses.

Request Body:

```json
{}
```

Response Body:

```json
{
  "success": true,
  "message": "Expenses retrieved",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `401 Unauthorized`, `500 Internal Server Error`

### POST /expenses

Purpose: Create an expense.

Request Body:

```json
{
  "placeholder": "expense payload"
}
```

Response Body:

```json
{
  "success": true,
  "message": "Expense created",
  "data": {}
}
```

HTTP Status Codes: `201 Created`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `422 Unprocessable Entity`, `500 Internal Server Error`

## Reports

### GET /reports/dashboard

Purpose: Retrieve dashboard summary metrics.

Request Body:

```json
{}
```

Response Body:

```json
{
  "success": true,
  "message": "Dashboard report retrieved",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `401 Unauthorized`, `500 Internal Server Error`

### GET /reports/fleet

Purpose: Retrieve fleet report data.

Request Body:

```json
{}
```

Response Body:

```json
{
  "success": true,
  "message": "Fleet report retrieved",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `401 Unauthorized`, `500 Internal Server Error`

### GET /reports/cost

Purpose: Retrieve cost report data.

Request Body:

```json
{}
```

Response Body:

```json
{
  "success": true,
  "message": "Cost report retrieved",
  "data": {}
}
```

HTTP Status Codes: `200 OK`, `401 Unauthorized`, `500 Internal Server Error`
