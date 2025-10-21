"""
Script de utilidad para convertir archivos .doc problemáticos a .docx o .txt

Uso:
    python convertir_doc_a_docx.py "ruta/al/archivo.doc"
"""

import sys
from pathlib import Path
import shutil


def convertir_doc_a_docx(ruta_doc: str) -> str:
    """
    Convierte archivo .doc a .docx renombrándolo
    (funciona si el archivo ya es .docx internamente)
    """
    ruta = Path(ruta_doc)
    
    if not ruta.exists():
        print(f"❌ Error: Archivo no encontrado: {ruta}")
        return None
    
    if ruta.suffix.lower() not in ['.doc']:
        print(f"❌ Error: El archivo debe tener extensión .doc (actual: {ruta.suffix})")
        return None
    
    # Crear nueva ruta con extensión .docx
    ruta_docx = ruta.with_suffix('.docx')
    
    # Renombrar/copiar
    if ruta_docx.exists():
        print(f"⚠️ Advertencia: {ruta_docx.name} ya existe")
        respuesta = input("¿Sobrescribir? (s/n): ")
        if respuesta.lower() != 's':
            print("❌ Operación cancelada")
            return None
    
    try:
        # Simplemente renombrar
        shutil.copy2(ruta, ruta_docx)
        print(f"✅ Archivo convertido exitosamente:")
        print(f"   Original: {ruta}")
        print(f"   Nuevo:    {ruta_docx}")
        print(f"\n💡 Ahora puedes subir '{ruta_docx.name}' en la interfaz web")
        return str(ruta_docx)
    except Exception as e:
        print(f"❌ Error al convertir: {e}")
        return None


def convertir_doc_a_txt(ruta_doc: str) -> str:
    """
    Intenta extraer texto de .doc usando python-docx
    """
    try:
        import docx
    except ImportError:
        print("❌ python-docx no instalado")
        print("   Instala: pip install python-docx")
        return None
    
    ruta = Path(ruta_doc)
    
    if not ruta.exists():
        print(f"❌ Error: Archivo no encontrado: {ruta}")
        return None
    
    try:
        # Intentar leer con python-docx
        doc = docx.Document(ruta)
        texto = "\n".join([p.text for p in doc.paragraphs])
        
        # Guardar como .txt
        ruta_txt = ruta.with_suffix('.txt')
        
        with open(ruta_txt, 'w', encoding='utf-8') as f:
            f.write(texto)
        
        print(f"✅ Archivo convertido a texto exitosamente:")
        print(f"   Original: {ruta}")
        print(f"   Nuevo:    {ruta_txt}")
        print(f"\n💡 Ahora puedes subir '{ruta_txt.name}' en la interfaz web")
        return str(ruta_txt)
        
    except Exception as e:
        print(f"❌ Error al extraer texto: {e}")
        print("\n💡 Intenta abrir el archivo en Word y guardarlo como .txt manualmente")
        return None


def main():
    """Función principal"""
    print("🔧 Convertidor de Archivos .doc Problemáticos")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("\n❌ Error: Debes proporcionar la ruta del archivo")
        print("\nUso:")
        print('  python convertir_doc_a_docx.py "ruta/al/archivo.doc"')
        print("\nEjemplo:")
        print('  python convertir_doc_a_docx.py "temp/Ins - 3255 - PIÑA - V3.doc"')
        return
    
    ruta_doc = sys.argv[1]
    
    print(f"\n📄 Archivo a convertir: {ruta_doc}")
    print("\nOpciones:")
    print("  1. Renombrar a .docx (rápido)")
    print("  2. Extraer texto y guardar como .txt (recomendado)")
    print("  3. Cancelar")
    
    opcion = input("\nSelecciona una opción (1/2/3): ")
    
    if opcion == "1":
        print("\n🔄 Renombrando a .docx...")
        convertir_doc_a_docx(ruta_doc)
    elif opcion == "2":
        print("\n🔄 Extrayendo texto a .txt...")
        convertir_doc_a_txt(ruta_doc)
    else:
        print("\n❌ Operación cancelada")


if __name__ == "__main__":
    main()

