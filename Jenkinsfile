pipeline {
  agent any

  environment {
    IMAGE_NAME = 'your-docker-registry/mario-game'
    IMAGE_TAG = "${env.BUILD_NUMBER}"
    CONTAINER_NAME = 'mario-game'
    DOCKER_CREDENTIALS_ID = 'docker-registry-credentials'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Install Dependencies') {
      steps {
        sh 'python3 -m pip install --upgrade pip'
        sh 'pip3 install -r requirements.txt'
      }
    }

    stage('Static Checks') {
      steps {
        sh 'python3 -m py_compile mario_like_game.py'
      }
    }

    stage('Mend Scan') {
      steps {
        sh '''
          echo "Running Mend scan..."
          # Example:
          # mend auth --token $MEND_TOKEN
          # mend scan --project-name mario-game --path .
        '''
      }
    }

    stage('Fortify Scan') {
      steps {
        sh '''
          echo "Running Fortify SAST scan..."
          # Example:
          # sourceanalyzer -b mario-game-build python3 -m py_compile mario_like_game.py
          # sourceanalyzer -b mario-game-build -scan -f mario-game.fpr
        '''
      }
    }

    stage('Build Docker Image') {
      steps {
        sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .'
        sh 'docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest'
      }
    }

    stage('Push Docker Image') {
      steps {
        withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDENTIALS_ID, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
          sh 'docker push ${IMAGE_NAME}:${IMAGE_TAG}'
          sh 'docker push ${IMAGE_NAME}:latest'
        }
      }
    }

    stage('Deploy Docker Container (Direct)') {
      steps {
        sh '''
          docker rm -f ${CONTAINER_NAME} || true
          docker run -d \
            --name ${CONTAINER_NAME} \
            -e SDL_VIDEODRIVER=dummy \
            --restart unless-stopped \
            ${IMAGE_NAME}:${IMAGE_TAG}
        '''
      }
    }
  }

  post {
    success {
      echo 'Pipeline completed successfully. Container deployed directly via Docker.'
    }
    failure {
      echo 'Pipeline failed.'
    }
  }
}
