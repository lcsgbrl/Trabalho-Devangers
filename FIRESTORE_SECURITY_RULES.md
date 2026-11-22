### 🔒 Regras de Segurança do Firestore

#### 📋 Como Aplicar as Regras
1. Acesse o [Firebase Console](https://console.firebase.google.com)
2. Selecione seu projeto **"projeto-devangers"**
3. Vá em **Firestore Database** → **Rules** (aba)
4. **Cole o código abaixo** no editor
5. Clique em **Publish**

---

#### 🛡️ Regras de Segurança (Security Rules)

```firestore_rules
rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {

    /**
     * ============================================
     * FUNÇÕES AUXILIARES
     * ============================================
     */
    function isAuthenticated() {
      return request.auth != null;
    }

    function getUserData() {
      return get(/databases/$(database)/documents/usuarios/$(request.auth.uid)).data;
    }

    function getUserRole() {
      return getUserData().role;
    }

    function getUserInstituicaoId() {
      return getUserData().instituicao_id;
    }

    function isSameInstituicao(instId) {
      return isAuthenticated() && getUserInstituicaoId() == instId;
    }

    function isAdmin() {
      return isAuthenticated() && (
        getUserRole() == 'admin' ||
        getUserRole() == 'Administrador' ||
        getUserRole() == 'Coordenador'
      );
    }

    function isProfessor() {
      return isAuthenticated() && (
        getUserRole() == 'professor' ||
        getUserRole() == 'Professor'
      );
    }

    function isOwner(uid) {
      return isAuthenticated() && request.auth.uid == uid;
    }

    /**
     * ============================================
     * COLEÇÃO: instituicoes
     * ============================================
     */
    match /instituicoes/{instId} {
      allow read: if isAuthenticated();
      allow write: if false; // Gerenciado apenas via Admin SDK / Console
    }

    /**
     * ============================================
     * COLEÇÃO: usuarios (chave: uid)
     * ============================================
     */
    match /usuarios/{uid} {
      // Leitura: próprio perfil ou admin da mesma instituição
      allow read: if isOwner(uid) || (
        isAdmin() && isSameInstituicao(resource.data.instituicao_id)
      );

      // Criação: apenas via pré-cadastro administrativo (Admin SDK)
      allow create: if false;

      // Atualização: próprio usuário (sem alterar role/instituicao_id) ou admin da mesma instituição
      allow update: if (
        isOwner(uid) &&
        request.resource.data.role == resource.data.role &&
        request.resource.data.instituicao_id == resource.data.instituicao_id
      ) || (
        isAdmin() && isSameInstituicao(resource.data.instituicao_id)
      );

      // Exclusão: próprio usuário ou admin da mesma instituição
      allow delete: if isOwner(uid) || (
        isAdmin() && isSameInstituicao(resource.data.instituicao_id)
      );
    }

    /**
     * ============================================
     * COLEÇÃO: membros (isolada por instituicao_id)
     * ============================================
     */
    match /membros/{docId} {
      allow read: if isSameInstituicao(resource.data.instituicao_id);

      allow create, delete: if isAdmin() &&
        isSameInstituicao(request.resource.data.instituicao_id);

      allow update: if isSameInstituicao(resource.data.instituicao_id) && (
        isAdmin() ||
        resource.data.email == request.auth.token.email
      );
    }

    /**
     * ============================================
     * COLEÇÃO: salas (isolada por instituicao_id)
     * ============================================
     */
    match /salas/{docId} {
      allow read: if isSameInstituicao(resource.data.instituicao_id);

      allow create: if isAdmin() &&
        isSameInstituicao(request.resource.data.instituicao_id);

      allow update, delete: if isAdmin() &&
        isSameInstituicao(resource.data.instituicao_id);
    }

    /**
     * ============================================
     * COLEÇÃO: solicitacoes (isolada por instituicao_id)
     * ============================================
     */
    match /solicitacoes/{docId} {
      allow read: if isSameInstituicao(resource.data.instituicao_id);

      allow create: if isSameInstituicao(request.resource.data.instituicao_id);

      allow update: if isSameInstituicao(resource.data.instituicao_id) && (
        isAdmin() ||
        isProfessor() ||
        resource.data.solicitanteUid == request.auth.uid
      );

      allow delete: if isAdmin() &&
        isSameInstituicao(resource.data.instituicao_id);
    }

    /**
     * ============================================
     * COLEÇÕES ACADÊMICAS (isoladas por instituicao_id)
     * academico_nucleos, academico_cursos,
     * academico_turmas, academico_disciplinas
     * ============================================
     */
    match /{colecaoAcademica}/{docId} {
      allow read: if colecaoAcademica in [
        'academico_nucleos',
        'academico_cursos',
        'academico_turmas',
        'academico_disciplinas'
      ] && isSameInstituicao(resource.data.instituicao_id);

      allow create: if colecaoAcademica in [
        'academico_nucleos',
        'academico_cursos',
        'academico_turmas',
        'academico_disciplinas'
      ] && isAdmin() && isSameInstituicao(request.resource.data.instituicao_id);

      allow update, delete: if colecaoAcademica in [
        'academico_nucleos',
        'academico_cursos',
        'academico_turmas',
        'academico_disciplinas'
      ] && isAdmin() && isSameInstituicao(resource.data.instituicao_id);
    }

    /**
     * ============================================
     * REGRA PADRÃO: NEGAR TUDO O QUE NÃO FOI EXPLICITADO
     * ============================================
     */
    match /{document=**} {
      allow read, write: if false;
    }
  }
}