 node {
   environment {
        DOCKER_REPO = "fcaudillo/tpv-verde"
        DOCKER_CREDENTIAL = "dockerhub"
   }   
   stage('Git checkout') {
       git 'https://github.com/fcaudillo/TPVBelleza.git'
   }
   
   stage('Construyendo imagen') {
       sh ('docker build --build-arg BUILD_USU_MQ=${USUARIO_MQ} --build-arg BUILD_PASS_MQ=${PASSWORD_MQ} --build-arg BUILD_CLIENTE_ID=${CLIENTE_ID} -t  fcaudillo/tpv-verde:lts . ') 
   }
  
   stage('Subiendo la imagen.') {
        withDockerRegistry([ credentialsId: "my_crends_docker", url: '' ]) {   
           sh "docker push fcaudillo/tpv-verde:lts "    
           
       }    
   }
   
   stage('Deploy a produccion') {
       sh "cd main && docker-compose stop tlapape"
       sh "docker run -v /home/dockeradm/data/tpv-verde:/app/tlapape/data --rm fcaudillo/tpv-verde:lts ./manage.py migrate " 
       sh "cd main && docker-compose up -d --no-deps --build tlapape"
   }

}
