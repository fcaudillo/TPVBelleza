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
       sh ('docker build -t  ${env.DOCKER_REPO}:lts . ')
       
   }
}
