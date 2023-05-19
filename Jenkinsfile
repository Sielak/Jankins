pipeline {
    agent {
        label "master"
    }
	options {
      gitLabConnection('gitlab')
      gitlabBuilds(builds: ['Build', 'Test', 'Deploy'])
    }
    stages {
        stage('Build') {
            steps {
                updateGitlabCommitStatus name: 'Build', state: 'pending'
                bat "pip install -r requirements.txt"
                updateGitlabCommitStatus name: 'Build', state: 'success'
            }
        }
		stage('Test') {
            steps {
                updateGitlabCommitStatus name: 'Test', state: 'pending'
                echo "This is test  stage"
                echo env.BRANCH_NAME
            }
			post {
				failure {
                    updateGitlabCommitStatus name: 'Test', state: 'failed'
				}
                success {
                    updateGitlabCommitStatus name: 'Test', state: 'success'
				}
			}
        }
        stage('Deploy') {
            when { 
                equals expected: 'main', 
                actual: env.BRANCH_NAME 
            }
            steps {
                updateGitlabCommitStatus name: 'Deploy', state: 'pending'
                bat "xcopy * C:\\jenkins\\jenkins_scripts /y /s /i"
                echo 'New version installed'
                updateGitlabCommitStatus name: 'Deploy', state: 'success'
            }
        }
		stage('Deploy - dev') {
            when { 
                not { 
                    equals expected: 'main', 
                    actual: env.BRANCH_NAME 
                } 
            }
            steps {
                updateGitlabCommitStatus name: 'Deploy', state: 'pending'
                updateGitlabCommitStatus name: 'Deploy', state: 'success'
            }
        }
    }
	post {
        always {
            cleanWs deleteDirs: true, notFailBuild: true
        }
		failure{			
			emailext body: "Job Failed<br>URL: ${env.BUILD_URL}", 
                    recipientProviders: [[$class: 'DevelopersRecipientProvider']],
					subject: "Job: ${env.JOB_NAME}, Build: #${env.BUILD_NUMBER} - Failure !",
					attachLog: true
        }
        success{			
			emailext body: "Job builded<br>URL: ${env.BUILD_URL}", 
                    recipientProviders: [[$class: 'DevelopersRecipientProvider']],
					subject: "Job: ${env.JOB_NAME}, Build: #${env.BUILD_NUMBER} - Success !",
					attachLog: true
        }
    }
}
