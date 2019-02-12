#!groovy

pipeline {
    agent any
    stages {
        stage('Building') {
            steps {
                echo 'Stage: Building...'
                sh "pipeline/build.sh"
            }
        }
        stage('Style check') {
            steps {
                echo 'Stage: Style check...'
                sh "pipeline/checkstyle.sh"
            }
        }
        stage('Testing') {
            steps {
                echo 'Stage: Testing...'
                sh "pipeline/test.sh"
            }
        }
        stage('Publication') {
            steps {
                echo 'Stage: Publication...'
                sh "pipeline/publish.sh"
            }
        }
        stage('Cleaning') {
            steps {
                echo 'Stage: Cleaning...'
                sh "pipeline/clean.sh"
            }
        }
    }

    post {
        success {
            emailext(from: "jenkins@sonata-nfv.eu", 
            to: "askhat.nuriddinov@ugent.be", 
            subject: "SUCCESS: ${env.JOB_NAME}/${env.BUILD_ID} (${env.BRANCH_NAME})",
            body: "${env.JOB_URL}")
        }
        failure {
            emailext(from: "jenkins@sonata-nfv.eu", 
            to: "askhat.nuriddinov@ugent.be", 
            subject: "FAILURE: ${env.JOB_NAME}/${env.BUILD_ID} (${env.BRANCH_NAME})",
            body: "${env.JOB_URL}")
        }
    }
}
