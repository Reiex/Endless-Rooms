uniform sampler2D texture;
uniform vec2 bloc, bloc_haut, bloc_bas, bloc_gauche, bloc_droite, bloc_haut_gauche, bloc_haut_droite, bloc_bas_gauche, bloc_bas_droite;
uniform vec2 pos_bloc;
uniform float taille_texture;

void main()
{
    vec4 pixel = texture2D(texture, gl_TexCoord[0].xy);
	vec2 pos_pixel = vec2(gl_FragCoord.x-pos_bloc.x, (taille_texture-gl_FragCoord.y)-pos_bloc.y);
	vec2 inv_pos_pixel = vec2(64.0 - pos_pixel.x, 64.0 - pos_pixel.y);
	float masque = 1.0, masque_lave = 1.0;

	// CALCULER LE MASQUE DU PIXEL

	if(bloc[0] == 0.0)
	{
		// BLOCS ADJACENTS

		// Bloc de gauche
		if(bloc_gauche[0] == 1.0 && (4.0*pos_pixel.x) / 256.0 < masque){
			masque = (4.0*pos_pixel.x) / 256.0;
		}

		// Bloc de droite
		if(bloc_droite[0] == 1.0 && (4.0*inv_pos_pixel.x) / 256.0 < masque){
			masque = (4.0*inv_pos_pixel.x) / 256.0;
		}

		// Bloc du dessus
		if(bloc_haut[0] == 1.0 && (4.0*pos_pixel.y) / 256.0 < masque){
			masque = (4.0*pos_pixel.y) / 256.0;
		}

		// Bloc du dessous
		if(bloc_bas[0] == 1.0 && (4.0*inv_pos_pixel.y) / 256.0 < masque){
			masque = (4.0*inv_pos_pixel.y) / 256.0;
		}

		// BLOCS DIAGONAUX

		// Bloc en gaut à gauche
		if(bloc_haut_gauche[0] == 1.0 && bloc_haut[0] == 0.0 && bloc_gauche[0] == 0.0){
			if((4.0*pos_pixel.y) / 256.0 < masque && (4.0*pos_pixel.y) / 256.0 >= (4.0*pos_pixel.x) / 256.0){
				masque = (4.0*pos_pixel.y) / 256.0;
			}
			if((4.0*pos_pixel.x) / 256.0 < masque && (4.0*pos_pixel.x) / 256.0 >= (4.0*pos_pixel.y) / 256.0){
				masque = (4.0*pos_pixel.x) / 256.0;
			}
		}

		// Bloc en haut à droite
		if(bloc_haut_droite[0] == 1.0 && bloc_haut[0] == 0.0 && bloc_droite[0] == 0.0){
			if((4.0*pos_pixel.y) / 256.0 < masque && (4.0*pos_pixel.y) / 256.0 >= (4.0*inv_pos_pixel.x) / 256.0){
				masque = (4.0*pos_pixel.y) / 256.0;
			}
			if((4.0*inv_pos_pixel.x) / 256.0 < masque && (4.0*inv_pos_pixel.x) / 256.0 >= (4.0*pos_pixel.y) / 256.0){
				masque = (4.0*inv_pos_pixel.x) / 256.0;
			}
		}

		// Bloc en bas à gauche
		if(bloc_bas_gauche[0] == 1.0 && bloc_bas[0] == 0.0 && bloc_gauche[0] == 0.0){
			if((4.0*inv_pos_pixel.y) / 256.0 < masque && (4.0*inv_pos_pixel.y) / 256.0 >= (4.0*pos_pixel.x) / 256.0){
				masque = (4.0*inv_pos_pixel.y) / 256.0;
			}
			if((4.0*pos_pixel.x) / 256.0 < masque && (4.0*pos_pixel.x) / 256.0 >= (4.0*inv_pos_pixel.y) / 256.0){
				masque = (4.0*pos_pixel.x) / 256.0;
			}
		}

		// Bloc en bas à droite
		if(bloc_bas_droite[0] == 1.0 && bloc_bas[0] == 0.0 && bloc_droite[0] == 0.0){
			if((4.0*inv_pos_pixel.y) / 256.0 < masque && (4.0*inv_pos_pixel.y) / 256.0 >= (4.0*inv_pos_pixel.x) / 256.0){
				masque = (4.0*inv_pos_pixel.y) / 256.0;
			}
			if((4.0*inv_pos_pixel.x) / 256.0 < masque && (4.0*inv_pos_pixel.x) / 256.0 >= (4.0*inv_pos_pixel.y) / 256.0){
				masque = (4.0*inv_pos_pixel.x) / 256.0;
			}
		}
	}
	else
	{
		masque = 0.0;
	}

	// CALCULER LE MASQUE LAVE, INDIQUANT LA PUISSANCE DE LA LUMIERE EMISE PAR LA LAVE PROCHE

	// BLOCS ADJACENTS

	// Bloc de gauche
	if(bloc_gauche[1] == 8 && (4.0*pos_pixel.x) / 256.0 < masque_lave){
		masque_lave = (4.0*pos_pixel.x) / 256.0;
	}

	// Bloc de droite
	if(bloc_droite[1] == 8 && (4.0*inv_pos_pixel.x) / 256.0 < masque_lave){
		masque_lave = (4.0*inv_pos_pixel.x) / 256.0;
	}

	// Bloc du dessus
	if(bloc_haut[1] == 8 && (4.0*pos_pixel.y) / 256.0 < masque_lave){
		masque_lave = (4.0*pos_pixel.y) / 256.0;
	}

	// Bloc du dessous
	if(bloc_bas[1] == 8 && (4.0*inv_pos_pixel.y) / 256.0 < masque_lave){
		masque_lave = (4.0*inv_pos_pixel.y) / 256.0;
	}

	// BLOCS DIAGONAUX

	// Bloc en gaut à gauche
	if(bloc_haut_gauche[1] == 8 && bloc_haut[1] != 8 && bloc_gauche[1] != 8){
		if((4.0*pos_pixel.y) / 256.0 < masque_lave && (4.0*pos_pixel.y) / 256.0 >= (4.0*pos_pixel.x) / 256.0){
			masque_lave = (4.0*pos_pixel.y) / 256.0;
		}
		if((4.0*pos_pixel.x) / 256.0 < masque_lave && (4.0*pos_pixel.x) / 256.0 >= (4.0*pos_pixel.y) / 256.0){
			masque_lave = (4.0*pos_pixel.x) / 256.0;
		}
	}

	// Bloc en haut à droite
	if(bloc_haut_droite[1] == 8 && bloc_haut[1] != 8 && bloc_droite[1] != 8){
		if((4.0*pos_pixel.y) / 256.0 < masque_lave && (4.0*pos_pixel.y) / 256.0 >= (4.0*inv_pos_pixel.x) / 256.0){
			masque_lave = (4.0*pos_pixel.y) / 256.0;
		}
		if((4.0*inv_pos_pixel.x) / 256.0 < masque_lave && (4.0*inv_pos_pixel.x) / 256.0 >= (4.0*pos_pixel.y) / 256.0){
			masque_lave = (4.0*inv_pos_pixel.x) / 256.0;
		}
	}

	// Bloc en bas à gauche
	if(bloc_bas_gauche[1] == 8 && bloc_bas[1] != 8 && bloc_gauche[1] != 8){
		if((4.0*inv_pos_pixel.y) / 256.0 < masque_lave && (4.0*inv_pos_pixel.y) / 256.0 >= (4.0*pos_pixel.x) / 256.0){
			masque_lave = (4.0*inv_pos_pixel.y) / 256.0;
		}
		if((4.0*pos_pixel.x) / 256.0 < masque_lave && (4.0*pos_pixel.x) / 256.0 >= (4.0*inv_pos_pixel.y) / 256.0){
			masque_lave = (4.0*pos_pixel.x) / 256.0;
		}
	}

	// Bloc en bas à droite
	if(bloc_bas_droite[1] == 8 && bloc_bas[1] != 8 && bloc_droite[1] != 8){
		if((4.0*inv_pos_pixel.y) / 256.0 < masque_lave && (4.0*inv_pos_pixel.y) / 256.0 >= (4.0*inv_pos_pixel.x) / 256.0){
			masque_lave = (4.0*inv_pos_pixel.y) / 256.0;
		}
		if((4.0*inv_pos_pixel.x) / 256.0 < masque_lave && (4.0*inv_pos_pixel.x) / 256.0 >= (4.0*inv_pos_pixel.y) / 256.0){
			masque_lave = (4.0*inv_pos_pixel.x) / 256.0;
		}
	}

	// CALCULER LA COULEUR DU PIXEL

	//S'il est exposé à la lave
	if(masque_lave < 0.8){

		float r_ajout = (0.8 - masque_lave)/2;
		if(r_ajout < 0){
			r_ajout = 0;
		}

		gl_FragColor = vec4(pixel.r*(1.0 - masque)+0.05+r_ajout, pixel.g*(1.0 - masque)+0.05+r_ajout/6, pixel.b*(1.0 - masque)+0.05, pixel.a);
	}

	// S'il n'est pas exposé à la lave
	else{
		gl_FragColor = vec4(pixel.r*(1.0 - masque)+0.05, pixel.g*(1.0 - masque)+0.05, pixel.b*(1.0 - masque)+0.05, pixel.a);
	}
}
