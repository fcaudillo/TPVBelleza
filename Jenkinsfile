 node {
    
   stage('Git checkout') {
       
       git 'https://github.com/fcaudillo/TPVBelleza.git'
   }
   
   stage('Construyendo imagen') {

       sh ('ls')
       sh ('pwd')
       sh ('docker build -t tpv-verde . ')
       
   }
}
