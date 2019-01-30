 node {
   environment {
        DOCKER_REPO = "fcaudillo/tpv-verde"
        DOCKER_CREDENTIAL = "dockerhub"
  }   
   stage('Git checkout') {
       
       git 'https://github.com/fcaudillo/TPVBelleza.git'
   }
   
   stage('Construyendo imagen') {

       sh ('ls -larh')
       sh ('echo ${env.GIT_COMMIT} ')
       sh ('docker build -t  ${DOCKER_REPO}:lts . ')
       
   }
}
