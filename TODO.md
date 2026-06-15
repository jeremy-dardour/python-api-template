# Create template:
- make scratchpad and memory work in real time - not taken into account so far and not working properly

- learn about best practices https://github.com/zhanymkanov/fastapi-best-practices#project-structure
- choose configuration management
  - No config layer. core/config.py with Pydantic BaseSettings is referenced in
  standards but doesn't exist, and FastAPI() is bare (no title, version, lifespan,
  docs gating). Configuration management is still an open TODO; it's foundational
  and blocks DB, auth, and observability.
- standard error responses
- choose http client lib
- server packaging?
- ci pipeline
    - dependency caching
    - security / dependency checks
- DB?

- implement
    - structured logging
    - CORS - rate limiting - ??
    - standard error responses - global exception handling
    - code style practices - formatting - typing -
    - auth?
    - structured logging with request IDs, global exception handler with a standard error envelope, CORS, rate limiting, health/readiness endpoints, security headers.
- Full coverage of endpoint with failure cases
- example of unit testing with override / api test with overidden external dep

- choose and implement observability
- choose and implement auth?
- health checks
- secret management strategy
- ci/cd pipeline
- conteneurisation?

# Done:

- choose package manager
- choose python version
- choose http framework
- have a basic hello world working
- choose linting
- choose formater
- choose type checker
- choose unit / blackbox testing
- choose runtime object validator
- CI
