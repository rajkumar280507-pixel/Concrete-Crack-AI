# Use Python 3.10 as base
FROM python:3.10

# Create a non-root user (good practice for HF Spaces)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set working directory
WORKDIR /home/user/app

# Copy requirements and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy the rest of the application
COPY --chown=user . .

# Set environment variables
ENV PORT=7860
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 7860

# Run the app
CMD ["python", "webapp/app.py"]
