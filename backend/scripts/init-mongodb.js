// MongoDB Initialization Script
// This script runs automatically when the container is first created

// Switch to turistando_db
db = db.getSiblingDB('turistando_db');

// Create collections with validation
db.createCollection('comentarios', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['pontoId', 'usuarioId', 'texto', 'createdAt'],
      properties: {
        pontoId: {
          bsonType: 'int',
          description: 'ID do ponto turístico (PostgreSQL reference)'
        },
        usuarioId: {
          bsonType: 'int',
          description: 'ID do usuário (PostgreSQL reference)'
        },
        texto: {
          bsonType: 'string',
          maxLength: 500,
          description: 'Texto do comentário'
        },
        createdAt: {
          bsonType: 'date',
          description: 'Data de criação'
        },
        respostas: {
          bsonType: 'array',
          description: 'Array de respostas'
        }
      }
    }
  }
});

db.createCollection('fotos', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['pontoId', 'path', 'createdAt'],
      properties: {
        pontoId: {
          bsonType: 'int',
          description: 'ID do ponto turístico'
        },
        usuarioId: {
          bsonType: 'int',
          description: 'ID do usuário que fez upload'
        },
        path: {
          bsonType: 'string',
          description: 'Caminho do arquivo'
        },
        thumbnailPath: {
          bsonType: 'string',
          description: 'Caminho da miniatura'
        },
        createdAt: {
          bsonType: 'date',
          description: 'Data de upload'
        }
      }
    }
  }
});

// Create indexes
db.comentarios.createIndex({ pontoId: 1 });
db.comentarios.createIndex({ usuarioId: 1 });
db.comentarios.createIndex({ createdAt: -1 });

db.fotos.createIndex({ pontoId: 1 });
db.fotos.createIndex({ usuarioId: 1 });
db.fotos.createIndex({ createdAt: -1 });

print('MongoDB initialized successfully!');
