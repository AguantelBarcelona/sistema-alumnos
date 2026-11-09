
 // Jenkinsfile - Pipeline de "Sistema Alumnos" (OCY1102)
 //
 // Pipeline con compilación, pruebas, documentación y trazabilidad.

pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    // >>> [A-TRIGGER] (Parte A, paso A4): aquí va el bloque "triggers"

    environment {
        // Entorno virtual dentro del workspace
        PIPENV_VENV_IN_PROJECT    = '1'
        PIPENV_IGNORE_VIRTUALENVS = '1'
        PIPENV_NOSPIN             = '1'
    }

    stages {
        stage('Build') {
            steps {
                script {
                    // Versión vinculada al build y al commit
                    def sha = sh(
                        returnStdout: true,
                        script: 'git rev-parse --short HEAD'
                    ).trim()

                    env.GIT_SHA = sha
                    env.APP_VERSION = "1.0.${env.BUILD_NUMBER}+${sha}"
                }

                echo "Versión de este build: ${env.APP_VERSION}"

                sh 'rm -rf .venv reports && mkdir -p reports'
                sh 'pipenv install --dev --deploy'
                sh 'pipenv run python -m compileall -q app.py'
            }
        }

        stage('Test') {
            steps {
                sh 'pipenv run pytest --junitxml=reports/junit.xml'
            }
            post {
                always {
                    junit allowEmptyResults: true,
                          testResults: 'reports/junit.xml'
                }
            }
        }

        // >>> [A-ETAPAS] (Parte A, paso A1):
        // Aquí van "Analyze" y "Dependency Management"

        // PARTE B3: Generación automática de documentación
        stage('Generate Documentation') {
            steps {
                catchError(
                    buildResult: 'UNSTABLE',
                    stageResult: 'UNSTABLE'
                ) {
                    sh '''#!/bin/bash
                        set -eu

                        mkdir -p reports
                        rm -rf docs/html reports/doxygen_warnings.log

                        doxygen Doxyfile

                        if [ -s reports/doxygen_warnings.log ]; then
                            echo "Doxygen encontró código sin documentar o mal documentado:"
                            cat reports/doxygen_warnings.log
                            exit 1
                        fi

                        echo "Documentación generada sin advertencias en docs/html"
                    '''
                }
            }

            post {
                always {
                    archiveArtifacts artifacts: 'docs/html/**',
                                     allowEmptyArchive: true
                }
            }
        }

        // PARTE B4: Control de versiones y trazabilidad
        stage('Version Control') {
            // Solo versionar builds exitosos
            // y excluir ejecuciones programadas
            when {
                allOf {
                    expression {
                        currentBuild.currentResult == 'SUCCESS'
                    }
                    not {
                        triggeredBy 'TimerTrigger'
                    }
                }
            }

            steps {
                // Generar el registro de trazabilidad
                sh 'bash scripts/trazabilidad.sh'

                // Recuperar credenciales seguras de Jenkins
                withCredentials([usernamePassword(
                    credentialsId: 'github-token',
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_TOKEN'
                )]) {
                    sh '''#!/bin/bash
                        set -eu

                        # Identificar los commits automáticos
                        git config user.name "Jenkins CI"
                        git config user.email "jenkins@localhost"

                        # Agregar la documentación generada
                        git add docs

                        # No crear commits innecesarios
                        if git diff --cached --quiet; then
                            echo "No hay cambios en docs/: nada que versionar"
                            exit 0
                        fi

                        # Crear commit automático
                        git commit -q -m "docs: documentación del build #${BUILD_NUMBER} (${APP_VERSION}) [skip ci]"

                        # Crear etiqueta de trazabilidad
                        git tag -a "build-${BUILD_NUMBER}-${GIT_SHA}" -m "Build ${BUILD_NUMBER} - versión ${APP_VERSION}"

                        # Configurar autenticación segura
                        # sin colocar el token en la URL
                        ASKPASS="$(mktemp)"
                        trap 'rm -f "$ASKPASS"' EXIT

                        printf '#!/bin/sh\\ncase "$1" in Username*) echo "$GIT_USER" ;; *) echo "$GIT_TOKEN" ;; esac\\n' > "$ASKPASS"

                        chmod 700 "$ASKPASS"

                        # Publicar documentación y etiquetas
                        GIT_ASKPASS="$ASKPASS" GIT_TERMINAL_PROMPT=0 git push origin HEAD:main --follow-tags
                    '''
                }
            }
        }

        // >>> [B-DEPLOY] (Parte B, paso B5):
        // Aquí va la etapa "Deploy"
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**',
                             allowEmptyArchive: true
        }

        // >>> [A-POST] (Parte A, paso A4):
        // Aquí van las alertas
    }
}

// >>> [A-FUNCION] (Parte A, paso A4):
// Aquí va la función notificar()
