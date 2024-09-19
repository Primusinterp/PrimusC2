# Use the nimlang/nim image as the base
FROM nimlang/nim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN apt update -y

RUN apt install python3-pip gcc-mingw-w64 -y

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

RUN wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list
RUN apt update && apt install terraform -y


RUN apt install wireguard -y


# Nimble install
RUN nimble install -y winim 
RUN nimble install -y shlex 
RUN nimble install -y terminaltables
RUN nimble install -y RC4
RUN nimble install -y puppy
RUN nimble install -y byteutils

WORKDIR /app/C2

# Run server.py when the container launches
CMD ["python3", "server.py"]