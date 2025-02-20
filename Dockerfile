services:
    web:
      build:
        context: .
        dockerfile: Dockerfile  # Ensure this points to the correct location
      ports:
        - "8000:8000"
  