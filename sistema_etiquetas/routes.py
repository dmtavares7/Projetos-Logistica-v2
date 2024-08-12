from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from models import DadosEtiqueta
from app import db
import psycopg2
from werkzeug.utils import secure_filename
import os
from sqlalchemy import desc
from config import Config

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/inserir', methods=['GET', 'POST'])
def inserir_dados():
    if request.method == 'POST':
        etiqueta = request.form['etiqueta']
        
        if DadosEtiqueta.query.filter_by(etiqueta=etiqueta).first():
            flash('Esta etiqueta já existe no banco de dados.', 'error')
            return redirect(url_for('main.inserir_dados'))
        
        try:
            conn = psycopg2.connect(Config.POSTGRES_URI)
            cur = conn.cursor()
            cur.execute("""
                SELECT p.barcode as Etiqueta, o.branch as Filial, o."protheusId" as "Pedido Protheus", 
                o."webId" as "Pedido WEB", io.invoice as "Nota Fiscal", io.invoice_value as "Valor da Nota Fiscal",
                io.invoice_key as "Chave da Nota Fiscal", o."totalVolumes" as "Total de Volumes", 
                o.shipping_company as Transportadora
                FROM logistics.pallets p
                JOIN logistics.volumes v ON v.id = p.volume_id
                JOIN logistics.orders o ON o.id = v.order_id
                JOIN logistics.invoice_orders io ON io.id = o.invoice_order_id
                WHERE p.barcode = %s
            """, (etiqueta,))
            result = cur.fetchone()
            cur.close()
            conn.close()

            if result:
                return render_template('confirmar_dados.html', dados=result)
            else:
                flash('Etiqueta não encontrada no banco de dados PostgreSQL.', 'error')
        except Exception as e:
            flash(f'Erro ao consultar o banco de dados: {str(e)}', 'error')

    return render_template('inserir_dados.html')

@main.route('/confirmar_insercao', methods=['POST'])
def confirmar_insercao():
    if request.method == 'POST':
        if 'fotos' not in request.files or 'videos' not in request.files:
            flash('É obrigatório fornecer pelo menos uma foto e um vídeo.', 'error')
            return redirect(url_for('main.inserir_dados'))

        fotos = request.files.getlist('fotos')
        videos = request.files.getlist('videos')

        if not fotos[0].filename or not videos[0].filename:
            flash('É obrigatório fornecer pelo menos uma foto e um vídeo.', 'error')
            return redirect(url_for('main.inserir_dados'))

        foto_paths = []
        video_paths = []
        
        # Criar diretórios se não existirem
        fotos_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'fotos')
        videos_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'videos')
        os.makedirs(fotos_dir, exist_ok=True)
        os.makedirs(videos_dir, exist_ok=True)
        
        for foto in fotos:
            if foto:
                filename = secure_filename(foto.filename)
                filepath = os.path.join('uploads', 'fotos', filename)
                full_path = os.path.join(current_app.root_path, 'static', filepath)
                foto.save(full_path)
                foto_paths.append(filepath)
        
        for video in videos:
            if video:
                filename = secure_filename(video.filename)
                filepath = os.path.join('uploads', 'videos', filename)
                full_path = os.path.join(current_app.root_path, 'static', filepath)
                video.save(full_path)
                video_paths.append(filepath)

        novo_dado = DadosEtiqueta(
            etiqueta=request.form['etiqueta'],
            filial=request.form['filial'],
            pedido_protheus=request.form['pedido_protheus'],
            pedido_web=request.form['pedido_web'],
            nota_fiscal=request.form['nota_fiscal'],
            valor_nota_fiscal=float(request.form['valor_nota_fiscal']),
            chave_nota_fiscal=request.form['chave_nota_fiscal'],
            total_volumes=int(request.form['total_volumes']),
            transportadora=request.form['transportadora'],
            fotos=','.join(foto_paths),
            videos=','.join(video_paths)
        )
        db.session.add(novo_dado)
        db.session.commit()
        
        flash('Dados inseridos com sucesso!', 'success')
        return redirect(url_for('main.inserir_dados'))

@main.route('/consultar', methods=['GET', 'POST'])
def consultar_dados():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    sort = request.args.get('sort', 'etiqueta')
    order = request.args.get('order', 'asc')

    if request.method == 'POST':
        consulta = request.form['consulta']
        query = DadosEtiqueta.query.filter(
            (DadosEtiqueta.etiqueta == consulta) |
            (DadosEtiqueta.pedido_protheus == consulta) |
            (DadosEtiqueta.pedido_web == consulta) |
            (DadosEtiqueta.nota_fiscal == consulta)
        )
    else:
        query = DadosEtiqueta.query

    if order == 'desc':
        query = query.order_by(desc(getattr(DadosEtiqueta, sort)))
    else:
        query = query.order_by(getattr(DadosEtiqueta, sort))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('consultar_dados.html', pagination=pagination, sort=sort, order=order)

@main.route('/visualizar/<int:id>', methods=['GET'])
def visualizar_pedido(id):
    pedido = DadosEtiqueta.query.get_or_404(id)
    fotos = pedido.fotos.split(',') if pedido.fotos else []
    videos = pedido.videos.split(',') if pedido.videos else []
    return render_template('visualizar_pedido.html', pedido=pedido, fotos=fotos, videos=videos)